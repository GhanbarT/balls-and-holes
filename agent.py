import random

from typing import Tuple, Optional, Set, List, Union, TYPE_CHECKING
import uuid

from consts import UP, RIGHT, DOWN, LEFT, AGENT, EMPTY, ORB, HOLE, FILLED_HOLE, LOCK, VISITED
from utils import get_new_position

if TYPE_CHECKING:
    from playground import Playground


class Agent:
    directions = (UP, RIGHT, DOWN, LEFT)

    def __init__(self,
                 position: Tuple[int, int],
                 agent_id: Optional[str] = None,
                 agent_type: int = 1,
                 field_of_view: int = 3,
                 visibility: list[list[str]] = None,
                 random_seed: Optional[int] = None,
                 battery: int = 30):
        self.agent_id = agent_id if agent_id is not None \
            else str(uuid.uuid4())  # Assign a random UUID if no ID is provided
        self.type = agent_type
        self.position = position
        self.field_of_view = field_of_view

        self.visibility = visibility if visibility is not None \
            else [[EMPTY] * field_of_view for _ in range(field_of_view)]
        self.visibility[field_of_view // 2][field_of_view // 2] = self.get_label()
        self.visited_cells = {self.position}
        self.friends = list()

        # initial direction, battery, has_ball
        self.direction = 'up'  # Initial direction (up, down, left, right)
        self.battery = battery
        self.has_ball = False

        # saved list positions
        self.hole_positions: list[Tuple[int, int]] = list()
        self.orb_positions: list[Tuple[int, int]] = list()
        self.filled_hole_positions: Set[Tuple[int, int]] = set()
        self.filled_by_me_hole_positions: Set[Tuple[int, int]] = set()

        self.target_position: Optional[Tuple[int, int]] = None
        self.is_a_random_target: bool = False
        self.is_new_road: bool = False

        # We use a common list for orbs and holes locked target positions (don't lock random target position)
        # I think this is enough and there will be no need to have two different lists
        self.locked_positions: list[Tuple[int, int]] = list()

        if random_seed:
            random.seed = random_seed

    def turn_clockwise(self) -> str:
        """
        Turns the agent clockwise.

        This method updates the agent's direction to the next one in the clockwise order (up -> right -> down -> left -> up).

        Returns:
            The new direction of the agent.
        """
        current_index = self.directions.index(self.direction)
        new_index = (current_index + 1) % len(self.directions)
        self.direction = self.directions[new_index]
        return self.direction

    def take_step_forward(self, environment: 'Playground') -> bool:
        """
        Moves the agent one step forward in its current direction.

        Args:
            environment: The Playground object that the agent is in.

        Returns:
            A boolean value indicating whether the operation was successful. Returns True if the agent moved successfully,
            and False if the operation failed (for example, if the desired position is not valid).
        """
        self.battery -= 1
        self.is_new_road = False

        new_position = get_new_position(self.direction, self.position)
        if environment.agent_enter_cell(new_position, self):
            self.position = new_position
            self.visited_cells.add(new_position)
            self.inform_friends_v2(VISITED, 1, [new_position])

        return True

    def take_ball(self, environment: 'Playground') -> bool:
        """
        The agent picks up a ball from its current position.

        Args:
            environment: The Playground object that the agent is in.

        Returns:
            A boolean value indicating whether the operation was successful. Returns True if the agent picked up a ball successfully,
            and False if the operation failed (for example, if the agent already has a ball or there is no ball at the agent's position).
        """
        # self.target_position = None
        if self.has_ball:
            return False
        if environment.pick_orb(self.position):
            self.has_ball = True
            self.orb_positions.remove(self.position)
            self.inform_friends_v2(ORB, -1, [self.position])
            return True
        return False

    def put_ball_in_hole(self, environment: 'Playground') -> bool:
        """
        The agent places a ball in a hole at its current position.

        Args:
            environment: The Playground object that the agent is in.

        Returns:
            A boolean value indicating whether the operation was successful. Returns True if the agent placed a ball in a hole successfully,
            and False if the operation failed (for example, if the agent does not have a ball or there is no hole at the agent's position).
        """
        if not self.has_ball:
            return False

        if environment.place_orb(self.position, self):
            self.has_ball = False
            self.hole_positions.remove(self.position)
            self.filled_by_me_hole_positions.add(self.position)
            self.inform_friends_v2(FILLED_HOLE, -1, [self.position])
            return True
        return False

    def see(self, visibility: list[list[str]]) -> 'Agent':
        """
        Updates the agent's visibility grid.

        Args:
            visibility: A 2D list representing the cells that the agent can currently see.
        """
        self.visibility = visibility
        return self

    def update_item_positions(self) -> None:
        """
        Updates the positions of the items (orbs and holes) that the agent can see.

        This method should be called after the agent's visibility grid is updated.
        """
        # Calculate the top-left position of the visibility grid in the playground
        top_left_x = self.position[0] - self.field_of_view // 2
        top_left_y = self.position[1] - self.field_of_view // 2

        # Iterate over each cell in the visibility grid
        for i in range(len(self.visibility)):
            for j in range(len(self.visibility[i])):
                # Calculate the actual position of the cell in the playground
                env_x, env_y = top_left_x + j, top_left_y + i
                if ORB in self.visibility[i][j] and (env_x, env_y) not in self.orb_positions:
                    self.orb_positions.append((env_x, env_y))
                if HOLE in self.visibility[i][j] and (env_x, env_y) not in self.hole_positions:
                    self.hole_positions.append((env_x, env_y))

                if FILLED_HOLE in self.visibility[i][j]:
                    self.filled_hole_positions.add((env_x, env_y))
                    if (env_x, env_y) in self.hole_positions:
                        self.hole_positions.remove((env_x, env_y))

                # remove the orb from the orb_positions list if the cell is empty and there is an orb in the cell,
                # or it is better to check this in `interact_with_environment` method?
                if EMPTY == self.visibility[i][j] and (env_x, env_y) in self.orb_positions:
                    self.orb_positions.remove((env_x, env_y))
                    self.inform_friends_v2(ORB, -1, [(env_x, env_y)])

        # note: we can send all data (orb, hole and filled hole) to friends here, is it a good idea?
        self.inform_friends_v2(ORB, 1, self.orb_positions)
        self.inform_friends_v2(HOLE, 1, self.hole_positions)
        self.inform_friends_v2(FILLED_HOLE, 1, list(self.filled_hole_positions))

    def add_friends(self, friends: Union['Agent', List['Agent']]) -> List['Agent']:
        """
        Adds friends to the agent's list of friends.

        Args:
            friends: An Agent instance or a list of Agent instances to be added to the friends list.

        Returns:
            The updated list of friends.
        """
        if isinstance(friends, Agent):
            friends = [friends]

        # Filter the incoming friends based on the current friends
        current_friend_ids = {friend.agent_id for friend in self.friends}
        new_friends = [friend for friend in friends if
                       friend.agent_id != self.agent_id and friend.agent_id not in current_friend_ids]

        self.friends.extend(new_friends)
        return self.friends

    def receive_friends_info_v2(self,
                                info_type: [ORB, HOLE, FILLED_HOLE, LOCK, VISITED],
                                status: [-1, 1],
                                positions: List[Tuple[int, int]]) -> 'Agent':
        """
        Receives information from friends and updates the agent's knowledge.

        Args:
            info_type: A string representing the type of information to be received.
                    types: ORB, HOLE, FILLED_HOLE, LOCK, VISITED
            status: A integer representing the status of the information
                    1: add the information to the friend's knowledge
                    -1: remove the information from the friend's knowledge
            positions: A list of tuples representing the positions of the items.

        Returns:
            The agent object itself.
        """
        if status == 1:
            if info_type == VISITED:
                self.visited_cells.update(positions)
            elif info_type == ORB:
                self.orb_positions += [pos for pos in positions if pos not in self.orb_positions]
            elif info_type == HOLE:
                self.hole_positions += [pos for pos in positions if pos not in self.hole_positions]
            elif info_type == FILLED_HOLE:
                # remove the filled hole from the hole_positions list
                self.hole_positions = [pos for pos in self.hole_positions if pos not in positions]
                self.filled_hole_positions.update(positions)
            elif info_type == LOCK:
                self.locked_positions += positions
        elif status == -1:
            if info_type == ORB:
                self.orb_positions = [pos for pos in self.orb_positions if pos not in positions]
            elif info_type == LOCK:
                self.locked_positions = [pos for pos in self.locked_positions if pos not in positions]
            # we don't have visited, hole and filled hole cell functionality

        return self

    def lock_cell(self, position: Tuple[int, int]) -> 'Agent':
        """
        Locks a cell to prevent other agents from interacting with it.

        Args:
            position: A tuple representing the position of the cell to be locked.

        Returns:
            The agent object itself.
        """
        self.locked_positions.append(position)
        self.inform_friends_v2(LOCK, 1, [position])
        return self

    def unlock_cell(self, position: Tuple[int, int]) -> 'Agent':
        """
        Unlocks a cell to allow other agents to interact with it.

        Args:
            position: A tuple representing the position of the cell to be unlocked.

        Returns:
            The agent object itself.
        """
        if position in self.locked_positions:
            self.locked_positions.remove(position)
            self.inform_friends_v2(LOCK, -1, [position])
        return self

    def inform_friends_v2(self,
                          info_type: [ORB, HOLE, FILLED_HOLE, VISITED],
                          status: [-1, 1],
                          positions: List[Tuple[int, int]]) -> 'Agent':
        """
        Informs friends about the agent's knowledge.

        Args:
            info_type: A string representing the type of information to be sent
                    types: ORB, HOLE, FILLED_HOLE, LOCK, VISITED
            status: A integer representing the status of the information
                    1: add the information to the friend's knowledge
                    -1: remove the information from the friend's knowledge
            positions: A list of tuples representing the positions of the items.

        Returns:
            The agent object itself.
        """
        for friend in self.friends:
            friend.receive_friends_info_v2(info_type, status, positions)

        return self

    def update_target(self, environment: 'Playground') -> None:
        """
        Updates the agent's target position.

        If the agent already has a target, and it is not a random target, this method does nothing.
        Otherwise, it sets the target to the nearest hole if the agent has a ball, or the nearest orb if the agent does not have a ball.
        If there are no available targets, it sets a random position in the playground as the target.
        """
        # TODO: it seems better to find nearest not-locked target every step.
        #  and also unlock previous target if it is locked and lock new target
        if self.target_position is not None and self.is_a_random_target is False:
            return

        # if the agent has a ball, the target is the nearest hole; otherwise, it is the nearest orb
        target_list = self.hole_positions if self.has_ball else self.orb_positions
        # remove locked positions from the target list
        target_list = [pos for pos in target_list if pos not in self.locked_positions]

        if len(target_list) > 0:
            self.target_position = self.find_nearest_target(target_list)
            self.is_a_random_target = False
            self.lock_cell(position=self.target_position)
        elif self.is_a_random_target is False:
            self.target_position = self.find_random_position(environment)
            self.is_a_random_target = True

    def find_nearest_target(self, target_list: list[Tuple[int, int]]) -> Tuple[int, int]:
        """
        Finds the nearest target to the agent from a list of potential targets.

        Args:
            target_list: A list of tuples, each containing two integers representing row and column indices.

        Returns:
            A tuple containing two integers representing the row and column indices of the nearest target.
        """
        nearest_target = min(target_list, key=lambda pos: Agent.manhattan_distance(self.position, pos))
        target_list.remove(nearest_target)
        return nearest_target

    def find_random_position(self, environment: 'Playground') -> Tuple[int, int]:
        """
        Finds a random position in the playground that the agent has not visited yet.

        Args:
            environment: The Playground object that the agent is in.

        Returns:
            A tuple containing two integers representing the row and column indices of the random position.
        """
        all_cell = set([(i, j) for i in range(environment.xAxis) for j in range(environment.yAxis)])
        reminded_cell = all_cell - self.visited_cells
        if len(reminded_cell) > 0:
            return random.choice(list(reminded_cell))
        else:
            # FIXME: it now can happened! because we have two agents and they can visit all cells
            # Logically, this should never happen! =))
            return self.visited_cells.pop()

    def interact_with_environment(self, environment: 'Playground') -> bool:
        """
        Allows the agent to interact with its environment.

        If the agent has a ball and is on a hole cell, it puts the ball in the hole.
        If the agent does not have a ball and is on an orb cell, it takes the ball.
        If the agent's current position is the target position, it resets the target position.

        Args:
            environment: The Playground object that the agent is in.

        Returns:
            A boolean value indicating whether the agent interacted with the environment. Returns True if the agent interacted with the environment,
            and False otherwise.
        """
        if self.has_ball and environment.is_a_hole_cell(self.position):
            self.unlock_cell(position=self.target_position)
            self.put_ball_in_hole(environment)
            return True
        if not self.has_ball and environment.is_a_orb_cell(self.position):
            self.unlock_cell(position=self.target_position)
            self.take_ball(environment)
            return True

        if self.target_position == self.position:
            #  check if current position is in the orb_positions list but there is no orb in the cell
            #  then the agent should remove the position from the orb_positions list and inform its friends,
            #  or we can do that in any update_item_positions run. (done!)
            self.unlock_cell(position=self.target_position)
            self.target_position = None
            self.is_a_random_target = False

        return False

    def action(self, environment: 'Playground') -> 'Agent':
        """
        Defines the agent's actions in its environment.

        The agent first updates its item positions. Then, it checks if it can interact with the environment.
        If the agent successfully interacts with the environment (i.e., picks up an orb or fills a hole), it updates the visibility of the playground and its item positions.
        If the agent does not interact with the environment, it updates its target position and moves towards it.

        The agent moves towards the target by turning in the appropriate direction and taking a step forward.

        Args:
            environment: The Playground object that the agent is in.

        Returns:
            The agent object itself.
        """
        self.update_item_positions()
        if self.interact_with_environment(environment):
            # updated items in playground (in agent position) so update the visibility
            self.visibility[self.field_of_view // 2][self.field_of_view // 2] = environment.get_cell_state(
                self.position)
            self.update_item_positions()
            return self

        # if battery = 0 -> move not allowed
        if self.battery <= 0:
            return self

        self.update_target(environment)
        if self.is_new_road:
            self.take_step_forward(environment)
            return self

        self.update_direction_towards_target()
        if self.is_agent_in_front():
            opposite_agent = self.get_opposite_agent()
            # vis_x, vis_y = self.get_front_cell_indices()
            with open('output.txt', 'a') as f:
                f.write(
                    f'{self.visibility};\ncurrent agent: {self};\nopposite agent: {opposite_agent}\n===============================\n')

            if not self.handle_opposite_agent(opposite_agent):
                return self

        self.take_step_forward(environment)
        return self

    def update_direction_towards_target(self) -> None:
        """
        Updates the agent's direction to move towards the target position.
        """
        target_x, target_y = self.target_position
        if self.position[0] < target_x:
            self.turn_to_direction(RIGHT)
        elif self.position[0] > target_x:
            self.turn_to_direction(LEFT)
        elif self.position[1] < target_y:
            self.turn_to_direction(DOWN)
        elif self.position[1] > target_y:
            self.turn_to_direction(UP)

    def turn_to_direction(self, direction: str) -> None:
        """
        Turns the agent to the given direction.
        """
        while self.direction != direction:
            self.turn_clockwise()

    def is_agent_in_front(self) -> bool:
        """
        Checks if another agent is in the front of the agent.

        Returns:
            A boolean value indicating whether another agent is in the front of the agent.
        """
        vis_x, vis_y = self.get_front_cell_indices()
        return AGENT in self.visibility[vis_y][vis_x]

    def get_opposite_agent(self) -> 'Agent':
        """
        Returns the opposite agent in the front of the agent.

        Returns:
            The opposite agent in the front of the agent.
        """
        vis_x, vis_y = self.get_front_cell_indices()
        return [friend for friend in self.friends if friend.get_label() in self.visibility[vis_y][vis_x]][0]

    def get_front_cell_indices(self) -> Tuple[int, int]:
        """
        Returns the indices of the cell in front of the agent based on its direction.

        Returns:
            A tuple containing two integers representing the row and column indices of the cell in front of the agent.
        """
        if self.direction == UP:
            return self.field_of_view // 2, self.field_of_view // 2 - 1
        elif self.direction == DOWN:
            return self.field_of_view // 2, self.field_of_view // 2 + 1
        elif self.direction == LEFT:
            return self.field_of_view // 2 - 1, self.field_of_view // 2
        elif self.direction == RIGHT:
            return self.field_of_view // 2 + 1, self.field_of_view // 2

    def handle_opposite_agent(self, opposite_agent: 'Agent') -> bool:
        """
        Handle the opposite agent.

        Args:
            opposite_agent: The opposite agent.

        Returns:
            A boolean value indicating whether the agent should move.
        """
        # if the other agent has no opposite direction of movement, wait one step (don't move).
        if not Agent.is_opposite_direction(self.direction, opposite_agent.direction):
            return False

        if not self.is_target_in_current_direction():
            self.change_direction_and_select_new_road()
            return True
        elif not opposite_agent.is_target_in_current_direction():
            opposite_agent.change_direction_and_select_new_road()
            opposite_agent.is_new_road = True
            return False
        elif self.battery > opposite_agent.battery:
            self.change_direction_and_select_new_road()
            return True
            # Important note: if the paths of both agents are opposite to each other,
            # we wait until the agent with more charge jumps or makes a decision.

    def is_target_in_current_direction(self) -> bool:
        """
        Checks if the target position is in the current direction of the agent.

        Returns:
            A boolean value indicating whether the target position is in the current direction of the agent.
        """
        if self.direction in [UP, DOWN]:
            return self.position[0] == self.target_position[0]
        else:
            return self.position[1] == self.target_position[1]

    def change_direction_and_select_new_road(self) -> None:
        """
        Changes the direction of the agent and selects a new road to move.

        The agent selects the road that is closest to the target position.
        """
        distances = []
        possible_directions = [direction for direction in self.directions if direction != self.direction]

        for direction in possible_directions:
            new_position = get_new_position(direction, self.position)
            distance = self.manhattan_distance(new_position, self.target_position)
            distances.append(distance)

        min_distance = min(distances)
        min_index = distances.index(min_distance)
        self.direction = self.directions[min_index]

    def get_label(self) -> str:
        """
        Returns the label of the agent.

        The label is a string that uniquely identifies the agent in the playground. It is composed of the string 'AGENT-' followed by the agent's ID.

        Returns:
            The label of the agent.
        """
        return AGENT + '-' + self.agent_id

    def get_my_score(self) -> int:
        """
        Returns the score of the agent.

        The score is calculated as the number of filled holes in the playground.

        Returns:
            The score of the agent.
        """
        return len(self.filled_by_me_hole_positions)

    def get_all_agents_score(self) -> int:
        """
        The score is calculated as the number of filled holes in the playground.

        Returns:
            The score of all agents.
        """
        return len(self.filled_hole_positions)

    def __str__(self):
        return f'Agent ID: {self.agent_id}, Type: {self.type}, Position: {self.position}, Target Position: {self.target_position}, Direction: {self.direction}, Battery: {self.battery}, Has Ball: {self.has_ball}, Score: {len(self.filled_by_me_hole_positions)}'

    @staticmethod
    def is_opposite_direction(direction1: str, direction2: str) -> bool:
        """
        Checks if two directions are opposite.

        Args:
            direction1: A string representing the first direction.
            direction2: A string representing the second direction.

        Returns:
            A boolean value indicating whether the two directions are opposite.
        """
        return direction1 == UP and direction2 == DOWN or \
            direction1 == DOWN and direction2 == UP or \
            direction1 == LEFT and direction2 == RIGHT or \
            direction1 == RIGHT and direction2 == LEFT

    @staticmethod
    def manhattan_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """
        Calculates the Manhattan distance between two positions.

        The Manhattan distance is the sum of the absolute differences of their coordinates. For example, the Manhattan distance between (1, 2) and (4, 6) is |1 - 4| + |2 - 6| = 3 + 4 = 7.

        Args:
            pos1: A tuple containing two integers representing the row and column indices of the first position.
            pos2: A tuple containing two integers representing the row and column indices of the second position.

        Returns:
            The Manhattan distance between the two positions.
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
