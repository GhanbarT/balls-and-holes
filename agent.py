import cmath
import random_seed

from typing import Tuple, Optional, Set, List, Union, TYPE_CHECKING
import uuid

from chatbot import Chatbot
from consts import UP, RIGHT, DOWN, LEFT, AGENT, EMPTY, ORB, HOLE, FILLED_HOLE, LOCK, GONE, VISITED
from utils import get_new_position

if TYPE_CHECKING:
    from playground import Playground

random = random_seed.RandomSeed().get_random_module()


class Agent:
    directions = (UP, RIGHT, DOWN, LEFT)

    def __init__(self,
                 position: Tuple[int, int],
                 agent_id: Optional[str] = None,
                 agent_type: int = 1,
                 field_of_view: int = 3,
                 visibility: list[list[str]] = None,
                 random_seed: Optional[int] = None,
                 battery: int = 30,
                 log_file: str = None,
                 chatbot: bool = True):
        self.agent_id = agent_id if agent_id is not None \
            else str(uuid.uuid4())  # Assign a random UUID if no ID is provided
        self.type = agent_type
        self.position = position
        self.field_of_view = field_of_view

        self.visibility = visibility if visibility is not None \
            else [[EMPTY] * field_of_view for _ in range(field_of_view)]
        self.visibility[field_of_view // 2][field_of_view // 2] = self.get_label()
        self.gone_cells = {self.position}
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

        self.log_file = log_file
        self.useLLM = chatbot
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
        self.is_new_road = False
        new_position = get_new_position(self.direction, self.position)
        if not environment.agent_enter_cell(new_position, self):
            return False

        self.position = new_position
        self.gone_cells.add(new_position)
        self.inform_friends_v2(GONE, 1, [new_position])
        self.battery -= 1

        return False

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

    def steal_ball_from_hole(self, environment: 'Playground') -> bool:
        """
        Attempts to steal a ball from a hole at the agent's current position.
        This method checks if the agent's current position is a filled hole. If it is, it checks if the hole was filled by the agent itself or one of its friends. If the hole was filled by another agent, it attempts to steal the ball from the hole.
        If the ball is successfully stolen, the method updates the agent's knowledge about the state of the hole (it is now unfilled) and informs its friends about the change.

        Args:
            environment: The Playground object that the agent is in.

        Returns:
            A boolean value indicating whether the operation was successful. Returns True if a ball was successfully stolen, and False otherwise (for example, if the agent's current position is not a filled hole, or the hole was filled by the agent itself or one of its friends).
        """
        if self.position not in self.filled_hole_positions or self.position not in environment.holes.keys():
            return False

        filler_agent_id = environment.holes[self.position]
        # check if the hole is filled by the agent's team friends then don't steal the ball
        if filler_agent_id == self.agent_id or filler_agent_id in [friend.agent_id for friend in self.friends]:
            return False
        if not environment.throw_orb_from_hole(self.position):
            return False

        self.filled_hole_positions.remove(self.position)
        self.hole_positions.append(self.position)
        self.inform_friends_v2(HOLE, 1, [self.position])
        self.inform_friends_v2(FILLED_HOLE, -1, [self.position])
        return True

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
                self.visited_cells.add((env_x, env_y))
                if ORB in self.visibility[i][j] and (env_x, env_y) not in self.orb_positions:
                    self.orb_positions.append((env_x, env_y))
                if HOLE in self.visibility[i][j] and (env_x, env_y) not in self.hole_positions:
                    self.hole_positions.append((env_x, env_y))

                if FILLED_HOLE in self.visibility[i][j]:
                    self.filled_hole_positions.add((env_x, env_y))
                    if (env_x, env_y) in self.hole_positions:
                        self.hole_positions.remove((env_x, env_y))

        # we can send all data (orb, hole and filled hole) to friends here, is it a good idea? or just send new items ...
        self.inform_friends_v2(VISITED, 1, list(self.visited_cells))
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
                                info_type: [ORB, HOLE, FILLED_HOLE, LOCK, GONE, VISITED],
                                status: [-1, 1],
                                positions: List[Tuple[int, int]]) -> 'Agent':
        """
        Receives information from friends and updates the agent's knowledge.

        Args:
            info_type: A string representing the type of information to be received.
                    types: ORB, HOLE, FILLED_HOLE, LOCK, GONE, VISITED
            status: A integer representing the status of the information
                    1: add the information to the friend's knowledge
                    -1: remove the information from the friend's knowledge
            positions: A list of tuples representing the positions of the items.

        Returns:
            The agent object itself.
        """
        if status == 1:
            if info_type == GONE:
                self.gone_cells.update(positions)
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

    def unlock_cell(self, position: Tuple[int, int] | None) -> 'Agent':
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
                          info_type: [ORB, HOLE, FILLED_HOLE, GONE, VISITED],
                          status: [-1, 1],
                          positions: List[Tuple[int, int]]) -> 'Agent':
        """
        Informs friends about the agent's knowledge.

        Args:
            info_type: A string representing the type of information to be sent
                    types: ORB, HOLE, FILLED_HOLE, LOCK, GONE, VISITED
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

    def get_memory_based_map(self, environment: 'Playground') -> list[list[str]]:
        """
        Generates a map based on the agent's memory and current knowledge of the environment.

        Args:
            environment: The Playground object representing the environment.

        Returns:
            A list of lists representing the map from the agent's perspective.
        """
        map_ = [[(EMPTY if (j, i) in self.visited_cells else '-') for j in range(environment.xAxis)] for i in
                range(environment.yAxis)]

        # Mark orbs, holes, and filled holes
        for orb_pos in self.orb_positions:
            self.mark_position(map_, orb_pos, ORB)
        for hole_pos in self.hole_positions:
            self.mark_position(map_, hole_pos, HOLE)
        for filled_hole_pos in self.filled_hole_positions:
            self.mark_position(map_, filled_hole_pos, FILLED_HOLE)

        # Mark the agent's position
        self.mark_position(map_, self.position, AGENT, combine=True)

        # Mark the positions of friends
        for friend in self.friends:
            if (friend.position[1] < environment.yAxis) and (friend.position[0] < environment.xAxis):
                self.mark_position(map_, friend.position, friend.get_label(), combine=True)

        return map_

    def update_target(self, environment: 'Playground') -> None:
        """
        Updates the agent's target position.

        The agent sets the target to the nearest hole if the agent has a ball, or the nearest orb if the agent does not have a ball.
        If there are no available targets, it sets a random position in the playground as the target.
        """

        prompt = f"""
I am an agent in a game where the objective is to find orbs(=balls), pick them up, and place them into holes. My field of view is limited to the 8 cells surrounding me. I can only carry one orb at a time.
In order to pick up an orb, I have to enter the cell (house) where the orb is located. And also, to put the ball in a hole, I have to enter the hole house.
Here are the possible states for each cell in the game:
    1. `empty`: The cell is empty.
    2. `hole`: The cell contains a hole.
    3. `orb`: The cell contains an orb.
    4. `filled_hole`: The cell contains a filled hole.
    5. `agent-[id]`: The cell contains an agent with the specified ID.
    6. `-`: There is no information about the cell.

This is the current state of the game map (size {environment.yAxis}*{environment.xAxis}) as I remember it:
{'\n'.join(' '.join('[' + format(str(item)).ljust(6, ' ') + ']' for item in row) for row in self.get_memory_based_map(environment))}

I can perform 4 actions: [UP, LEFT, DOWN, RIGHT].
Given that my flag in above map is <agent>, what is the best action for me to take to find the nearest {"hole" if self.has_ball else "orb"}?

Please note: If your previous answer did not affect the map, please provide a different answer.
Please provide your answer in the following format:
Answer: <action>
Reason: <reason>
        """

        error_counter = 0
        while self.useLLM:
            error_counter += 1

            try:
                answer = str(Chatbot().query(prompt, web_search=False))
            except KeyboardInterrupt:
                raise ValueError("Program interrupted by user.")
            except Exception as e:
                if error_counter > 3:
                    raise ValueError(e)
                continue

            direction = answer.split('\n')[0].replace('Answer: ', '').strip().upper()
            if direction not in ["UP", "LEFT", "DOWN", "RIGHT"]:
                print(f"Invalid action received from chatbot: {direction}")
                continue

            new_position = self.position
            current_x, current_y = self.position

            if direction == "UP":
                new_position = (current_x, current_y - 1)
            elif direction == "LEFT":
                new_position = (current_x - 1, current_y)
            elif direction == "DOWN":
                new_position = (current_x, current_y + 1)
            elif direction == "RIGHT":
                new_position = (current_x + 1, current_y)

            if self.log_file:
                with open(self.log_file, 'a') as f:
                    print(prompt, file=f)
                    print(f'answer: {answer} new position: {new_position}', file=f)
                    print('='*70, file=f)

            if environment.is_valid_position(new_position):
                self.target_position = new_position
                return

        # if the agent has a ball, the target is the nearest hole; otherwise, it is the nearest orb
        target_list = self.hole_positions if self.has_ball else self.orb_positions

        # if item in target position was removed by other agent, we must select new target
        if self.target_position not in target_list and self.is_a_random_target is False:
            self.reset_target_position()

        # remove locked positions from the target list
        target_list = [pos for pos in target_list if pos not in self.locked_positions]

        if len(target_list) > 0:
            nearest_target = self.find_nearest_target(target_list)
            # If the agent doesn't have a specific target or the new target is closer than the current target, update the target
            if (self.target_position is None or self.is_a_random_target or
                    Agent.manhattan_distance(self.position, nearest_target) <
                    Agent.manhattan_distance(self.position, self.target_position)):
                self.reset_target_position()
                self.target_position = nearest_target
                self.lock_cell(position=self.target_position)
        elif self.is_a_random_target is False and self.target_position is None:
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
        if len(reminded_cell) == 0:
            reminded_cell = all_cell - self.gone_cells

        if len(reminded_cell) > 0:
            return random.choice(list(reminded_cell))
        else:
            # it now can happen! because we have two agents, and they can visit all cells
            return random.choice(list(self.gone_cells))

    def reset_target_position(self) -> None:
        """
        Resets the target position of the agent.
        If the agent has a target position, it resets the target position and sets the is_a_random_target flag to False.
        """
        self.unlock_cell(position=self.target_position)
        self.target_position = None
        self.is_a_random_target = False

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
        # remove the orb from the orb_positions list if the cell is empty and there is an orb in the cell,
        # for example, another agent has taken the orb or the orb has been switched position
        self.steal_ball_from_hole(environment)
        if self.position in self.orb_positions and not environment.is_a_orb_cell(self.position):
            self.orb_positions.remove(self.position)
            self.inform_friends_v2(ORB, -1, [self.position])

        if self.has_ball and environment.is_a_hole_cell(self.position):
            self.reset_target_position()
            return self.put_ball_in_hole(environment)
        if not self.has_ball and environment.is_a_orb_cell(self.position):
            self.reset_target_position()
            return self.take_ball(environment)

        if self.target_position == self.position:
            self.reset_target_position()

        return False

    def action(self, environment: 'Playground', opposite_agent: 'Agent') -> 'Agent':
        """
        Defines the agent's actions in its environment.

        The agent first updates its item positions. Then, it checks if it can interact with the environment.
        If the agent successfully interacts with the environment (i.e., picks up an orb or fills a hole), it updates the visibility of the playground and its item positions.
        If the agent does not interact with the environment, it updates its target position and moves towards it.

        The agent moves towards the target by turning in the appropriate direction and taking a step forward.

        Args:
            environment: The Playground object that the agent is in.
            opposite_agent: `there is no doc`.

        Returns:
            The agent object itself.
        """
        self.update_item_positions()
        if self.interact_with_environment(environment):
            # updated items in playground so update the visibility
            self.see(environment.get_surrounding_cells(self.position, self.field_of_view))
            self.update_item_positions()
            # self.update_target(environment)
            return self

        # if battery = 0 -> move not allowed
        if self.battery <= 0:
            if self.battery == 0:
                self.battery -= 1
            return self

        self.update_target(environment)
        if self.is_new_road:
            self.take_step_forward(environment)
            return self

        self.update_direction_towards_target()

        if opposite_agent:
            if not self.handle_opposite_agent(opposite_agent, environment):
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

    def handle_opposite_agent(self, opposite_agent: 'Agent', environment: 'Playground') -> bool:
        """
        Handle the opposite agent.

        Args:
            opposite_agent: The opposite agent.
            environment: The Playground object that the agent is in.

        Returns:
            A boolean value indicating whether the agent should move.
        """
        # if the other agent has no opposite direction of movement, wait one step (don't move).
        if not Agent.is_opposite_direction(self.direction,
                                           opposite_agent.direction) and not opposite_agent.finished_battery():
            return False

        if not self.is_target_in_current_direction() or opposite_agent.finished_battery():
            self.change_direction_and_select_new_road(environment)
            return True
        elif not opposite_agent.is_target_in_current_direction():
            opposite_agent.change_direction_and_select_new_road(environment)
            opposite_agent.is_new_road = True
            return False
        elif self.battery >= opposite_agent.battery:
            self.change_direction_and_select_new_road(environment)
            return True

        # Important note: if the paths of both agents are opposite to each other,
        # we wait until the agent with more charge jumps or makes a decision.
        return False

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

    def change_direction_and_select_new_road(self, environment: 'Playground') -> None:
        """
        Changes the direction of the agent and selects a new road to move.

        The agent selects the road that is closest to the target position.

        Args:
            environment: The Playground object that the agent is in.
        """
        distances = []
        possible_directions = [direction for direction in self.directions if direction != self.direction]

        for direction in possible_directions:
            new_position = get_new_position(direction, self.position)
            if not environment.is_valid_position(new_position):
                distances.append(cmath.inf)
                continue
            distance = self.manhattan_distance(new_position, self.target_position)
            distances.append(distance)

        min_distance = min(distances)
        min_index = distances.index(min_distance)
        self.direction = possible_directions[min_index]

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

    def finished_battery(self):
        return self.battery <= 0

    def log_collision(self, opposite_agent: 'Agent') -> None:
        with open(self.log_file, 'a') as f:
            f.write(
                f'-> Collision\n'
                f'{self.visibility};\n'
                f'current agent: {self};\n'
                f'opposite agent: {opposite_agent}\n'
                f'{"=" * 20}\n')

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

    @staticmethod
    def mark_position(map_, position, label, combine=False):
        x, y = position
        if combine and map_[y][x] != EMPTY:
            map_[y][x] += ',' + label
        else:
            map_[y][x] = label
