import random

from typing import Tuple, Optional, Set, List, Union, TYPE_CHECKING
import uuid

from consts import UP, RIGHT, DOWN, LEFT, AGENT, EMPTY, ORB, HOLE, FILLED_HOLE
from utils import get_new_position

if TYPE_CHECKING:
    from Playground import Playground


class Agent:
    directions = (UP, RIGHT, DOWN, LEFT)
    locked_position: Set[Tuple[int, int]] = set()

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
        self.visited_cell = {self.position}
        self.friends = list()

        # initial direction, battery, has_ball
        self.direction = 'up'  # Initial direction (up, down, left, right)
        self.battery = battery
        self.has_ball = False
        self.hole_positions: list[Tuple[int, int]] = list()
        self.orb_positions: list[Tuple[int, int]] = list()
        self.locked_positions: list[Tuple[int, int]] = list()
        self.filled_hole_positions: Set[Tuple[int, int]] = set()

        self.target_position: Optional[Tuple[int, int]] = None
        self.is_a_random_target: bool = False

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

        new_position = get_new_position(self.direction, self.position)
        if environment.agent_enter_cell(new_position, self):
            self.position = new_position
            self.visited_cell.add(new_position)

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
        # self.target_position = None
        if not self.has_ball:
            return False

        if environment.place_orb(self.position, self):
            self.has_ball = False
            self.hole_positions.remove(self.position)
            return True
        return False

    def see(self, visibility: list[list[str]]) -> None:
        """
        Updates the agent's visibility grid.

        Args:
            visibility: A 2D list representing the cells that the agent can currently see.
        """
        self.visibility = visibility

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

        # Add each friend to the agent's list of friends, excluding the agent itself
        for friend in friends:
            if friend.agent_id != self.agent_id:
                self.friends.append(friend)

        return self.friends

    def receive_friend_info(self,
                            hole_positions: List[Tuple[int, int]],
                            orb_positions: List[Tuple[int, int]],
                            filled_hole_positions: Set[Tuple[int, int]]) -> 'Agent':
        """
        Receives information from friends and updates the agent's knowledge.

        Args:
            hole_positions: A list of tuples representing the positions of the holes.
            orb_positions: A list of tuples representing the positions of the orbs.
            filled_hole_positions: A set of tuples representing the positions of the filled holes.

        Returns:
            The agent object itself.
        """
        # Add or append the input arguments to the class variables
        self.hole_positions += [pos for pos in hole_positions if pos not in self.hole_positions]
        self.orb_positions += [pos for pos in orb_positions if pos not in self.orb_positions]
        self.filled_hole_positions.update(filled_hole_positions)

        return self

    def inform_friends(self) -> 'Agent':
        """
        Informs friends about the agent's knowledge.

        Returns:
            The agent object itself.
        """
        # FIXME: instead of sending all the information, we must send data on changing playground state
        #  for example, if the agent fills a hole, it should inform its friends about the filled hole and remove it from the hole_positions list
        #  or if the agent picks up an orb, it should inform its friends about the picked orb and remove it from the orb_positions list
        for friend in self.friends:
            friend.receive_friend_info(self.hole_positions, self.orb_positions, self.filled_hole_positions)

        return self

    def update_target(self, environment: 'Playground') -> None:
        """
        Updates the agent's target position.

        If the agent already has a target, and it is not a random target, this method does nothing.
        Otherwise, it sets the target to the nearest hole if the agent has a ball, or the nearest orb if the agent does not have a ball.
        If there are no available targets, it sets a random position in the playground as the target.
        """
        if self.target_position is not None and self.is_a_random_target is False:
            return

        target_list = self.hole_positions if self.has_ball else self.orb_positions

        if len(target_list) > 0:
            self.target_position = self.find_nearest_target(target_list)
            self.is_a_random_target = False
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
        # with open('output.txt', 'a') as f:
        #     f.write(f'find_random_position {self.visited_cell}\n')

        all_cell = set([(i, j) for i in range(environment.xAxis) for j in range(environment.yAxis)])
        reminded_cell = all_cell - self.visited_cell
        if len(reminded_cell) > 0:
            return random.choice(list(reminded_cell))
        else:
            # Logically, this should never happen! =]
            return self.visited_cell.pop()

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
        # TODO: add checking battery condition
        #   if batter = 0 -> move not allowed
        if self.has_ball and environment.is_a_hole_cell(self.position):
            self.put_ball_in_hole(environment)
            return True
        if not self.has_ball and environment.is_a_orb_cell(self.position):
            self.take_ball(environment)
            return True

        if self.target_position == self.position:
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

        self.update_target(environment)

        # TODO: check that state if agents reach together
        target_x, target_y = self.target_position
        if self.position[0] < target_x:
            while self.direction != RIGHT:
                self.turn_clockwise()
        elif self.position[0] > target_x:
            while self.direction != LEFT:
                self.turn_clockwise()
        elif self.position[1] < target_y:
            while self.direction != DOWN:
                self.turn_clockwise()
        elif self.position[1] > target_y:
            while self.direction != UP:
                self.turn_clockwise()
        self.take_step_forward(environment)

        return self

    def get_label(self) -> str:
        """
        Returns the label of the agent.

        The label is a string that uniquely identifies the agent in the playground. It is composed of the string 'AGENT-' followed by the agent's ID.

        Returns:
            The label of the agent.
        """
        return AGENT + '-' + self.agent_id

    def get_score(self) -> int:
        """
        Returns the score of the agent.

        The score is calculated as the number of filled holes in the playground.

        Returns:
            The score of the agent.
        """
        return len(self.filled_hole_positions)

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
