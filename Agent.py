import random

from typing import Tuple, Optional, TYPE_CHECKING, Set
import uuid

from consts import UP, RIGHT, DOWN, LEFT, AGENT, EMPTY, ORB, HOLE, FILLED_HOLE

if TYPE_CHECKING:
    from Playground import Playground

random.seed = 100


class Agent:
    directions = (UP, RIGHT, DOWN, LEFT)

    def __init__(self,
                 agent_id: Optional[str] = None,
                 position: Tuple[int, int] = (0, 0),
                 field_of_view: int = 3,
                 visibility: list[list[str]] = None):
        self.agent_id = agent_id if agent_id is not None \
            else str(uuid.uuid4())  # Assign a random UUID if no ID is provided
        self.position = position
        self.field_of_view = field_of_view

        self.visibility = visibility if visibility is not None \
            else [[EMPTY] * field_of_view for _ in range(field_of_view)]
        self.visibility[field_of_view // 2][field_of_view // 2] = self.get_label()
        self.visited_cell = {self.position}

        # initial direction, battery, has_ball
        self.direction = 'up'  # Initial direction (up, down, left, right)
        self.battery = 30
        self.has_ball = False
        self.hole_positions: list[Tuple[int, int]] = list()
        self.orb_positions: list[Tuple[int, int]] = list()

        self.target_position: Optional[Tuple[int, int]] = None
        self.is_a_random_target: bool = False
        self.filled_hole_positions: Set[Tuple[int, int]] = set()

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
        x, y = self.position

        # TODO: convert this code to a utility function
        new_position = None
        if self.direction == UP:
            new_position = (x, y - 1)
        elif self.direction == RIGHT:
            new_position = (x + 1, y)
        elif self.direction == DOWN:
            new_position = (x, y + 1)
        elif self.direction == LEFT:
            new_position = (x - 1, y)

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
        self.target_position = None
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
        self.target_position = None
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

        print(self.visibility)
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

        while True:
            random_position = (random.randint(0, environment.xAxis - 1), random.randint(0, environment.yAxis - 1))
            if random_position not in self.visited_cell:
                return random_position

    def action(self, environment: 'Playground'):
        self.update_item_positions()

        if self.target_position == self.position:
            if self.is_a_random_target:
                self.is_a_random_target = False
            elif self.has_ball:
                self.put_ball_in_hole(environment)
                return
            else:
                self.take_ball(environment)
                return

        self.update_target(environment)

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
