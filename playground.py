import random_seed
from typing import List, Tuple, Set, TYPE_CHECKING

from consts import EMPTY, HOLE, BALL, FILLED_HOLE, UP, RIGHT, DOWN, LEFT, AGENT
from utils import get_new_position

if TYPE_CHECKING:
    from agent import Agent

random = random_seed.RandomSeed().get_random_module()


class Playground:

    def __init__(self,
                 dimensions: Tuple[int, int] = (5, 5),
                 num_holes: int = 5,
                 num_balls: int = 5,
                 field_of_view: int = 3):
        self.dimensions = dimensions
        self.xAxis, self.yAxis = dimensions
        self.grid: list[list[str]] = [[EMPTY] * self.xAxis for _ in range(self.yAxis)]

        self.agent_start_positions: Set[Tuple[int, int]] = set()  # Store unique agent positions
        self.num_holes = num_holes
        self.num_balls = num_balls
        self.ball_positions = set()
        self.holes = {}

        self.field_of_view = field_of_view

    def add_agent(self, agent: 'Agent') -> bool:
        """
        Adds an agent to the playground.

        Args:
            agent: An Agent object. The agent should already have an ID, position, and field of view.

        Returns:
            A boolean value indicating whether the operation was successful. Returns True if the agent was added successfully,
            and False if the operation failed (for example, if the desired position is already occupied).
        """
        if agent.position in self.agent_start_positions:
            return False

        self.agent_start_positions.add(agent.position)  # Save the unique position
        x, y = agent.position
        self.grid[y][x] = agent.get_label()

        return True

    def get_random_empty_position(self) -> Tuple[int, int]:
        """
        Returns a random empty position in the playground.

        Returns:
            A tuple containing two integers representing row and column indices.
        """
        empty_positions = [(i, j) for i in range(self.xAxis) for j in range(self.yAxis) if self.grid[j][i] == EMPTY]
        return random.choice(empty_positions)

    def place_holes_and_balls(self) -> None:
        """
        Randomly places holes and balls (soil) on the grid, avoiding agent positions.

        The algorithm ensures that each position is unique and not already occupied by an agent.
        """
        available_positions = [(i, j) for i in range(self.xAxis) for j in range(self.yAxis) if
                               (i, j) not in self.agent_start_positions]
        random.shuffle(available_positions)

        # Place holes
        for i in range(self.num_holes):
            if len(available_positions) == 0:
                break
            x, y = available_positions.pop(0)
            self.grid[y][x] = HOLE
            self.holes[(x, y)] = ''

        # Place balls
        for i in range(self.num_balls):
            if len(available_positions) == 0:
                break
            x, y = available_positions.pop(0)
            self.grid[y][x] = BALL
            self.ball_positions.add((x, y))

    def get_surrounding_cells(self, position: Tuple[int, int], field_of_view: int = None) -> List[List[str]]:
        """
        Returns the status of the cells around the given position within the specified field of view.

        Args:
            position: A tuple containing two integers representing row and column indices.
            field_of_view: An integer representing the field of view. Value of the field of view must be an odd number;
                            Otherwise, it will be considered as the smallest number greater than the desired number.

        Returns:
            A list of lists representing the status of each cell.
        """
        if field_of_view is None:
            field_of_view = self.field_of_view

        x, y = position
        surrounding_cells = []

        for i in range(y - field_of_view // 2, y + field_of_view // 2 + 1):
            row = []
            for j in range(x - field_of_view // 2, x + field_of_view // 2 + 1):
                if i < 0 or j < 0 or i >= len(self.grid) or j >= len(self.grid[0]):
                    row.append('out')
                else:
                    row.append(self.grid[i][j])
            surrounding_cells.append(row)

        return surrounding_cells

    def get_cell_state(self, position: Tuple[int, int]) -> str:
        """
        Returns the state of the cell at the given position.

        Args:
            position: A tuple containing two integers representing row and column indices.

        Returns:
            The state of the cell at the given position.
        """
        x, y = position
        return self.grid[y][x]

    def agent_exit_cell(self, agent: 'Agent') -> None:
        """
        Updates the state of the cell that the agent is exiting.

        Args:
            agent: The Agent object that is exiting the cell.
        """
        current_cell_state = self.get_cell_state(agent.position)

        x, y = agent.position
        self.grid[y][x] = current_cell_state.replace(agent.get_label(), '').replace(',,', ',')

        if self.grid[y][x] == '':
            self.grid[y][x] = EMPTY
        # if last character is ',' remove that
        if self.grid[y][x][-1] == ',':
            self.grid[y][x] = self.grid[y][x][:-1]

    def agent_enter_cell(self, position: Tuple[int, int], agent: 'Agent') -> bool:
        """
        Updates the state of the cell that the agent is entering.

        Args:
            position: A tuple containing two integers representing row and column indices.
            agent: The Agent object that is entering the cell.

        Returns:
            A boolean value indicating whether the operation was successful. Returns True if the agent entered the cell successfully,
            and False if the operation failed (for example, if the desired position is not valid).
        """
        if not self.is_valid_position(position) or AGENT in self.get_cell_state(position):
            return False
        current_cell_state = self.get_cell_state(position)

        x, y = position
        self.agent_exit_cell(agent)
        self.grid[y][x] = current_cell_state + ',' + agent.get_label()
        return True

    def pick_ball(self, position: Tuple[int, int]) -> bool:
        """
        Picks up a ball from a given position in the playground.

        Args:
            position: A tuple containing two integers representing row and column indices.

        Returns:
            A boolean value indicating whether the operation was successful. Returns True if a ball was successfully picked up,
            and False if the operation failed (for example, if the desired position is not valid or there is no ball at the position).
        """
        if not self.is_valid_position(position):
            return False
        current_cell_state = self.get_cell_state(position)
        if BALL not in current_cell_state:
            return False

        x_old, y_old = position
        self.grid[y_old][x_old] = current_cell_state.replace(BALL, EMPTY)

        # remove current ball
        self.ball_positions.remove(position)
        return True

    def switch_ball_positions(self) -> None:
        """
        Randomly switches the positions of the balls in the playground.

        This method iterates over each ball in the playground. For each ball, it randomly selects a direction (up, right, down, or left)
        and attempts to move the ball in that direction. If the new position is valid and not already occupied by another ball or a filled hole,
        the ball is moved to the new position.
        """
        ball_position_temp = set(self.ball_positions)
        for ball in ball_position_temp:
            direction = random.choice([UP, RIGHT, DOWN, LEFT])
            prob = random.random()
            if prob > 0.1:
                continue

            x_old, y_old = ball
            new_position = get_new_position(direction, ball)
            if not self.is_valid_position(new_position):
                continue

            x_new, y_new = new_position
            new_cell_label = self.get_cell_state(new_position)
            # if new position is ball or filled hole cell nothing change
            if BALL in new_cell_label or FILLED_HOLE in new_cell_label:
                continue

            if EMPTY in new_cell_label:
                self.grid[y_old][x_old] = self.grid[y_old][x_old].replace(BALL, EMPTY)
                self.grid[y_new][x_new] = self.grid[y_new][x_new].replace(EMPTY, BALL)
                self.ball_positions.remove(ball)
                self.ball_positions.add(new_position)
            elif HOLE in new_cell_label:
                self.grid[y_old][x_old] = self.grid[y_old][x_old].replace(BALL, EMPTY)
                self.grid[y_new][x_new] = self.grid[y_new][x_new].replace(HOLE, FILLED_HOLE)
                self.ball_positions.remove(ball)

    def place_ball(self, position: Tuple[int, int], agent: 'Agent') -> bool:
        """
        Places a ball at a given position in the playground.

        Args:
            position: A tuple containing two integers representing row and column indices.
            agent: The Agent object that is placing the ball.

        Returns:
            A boolean value indicating whether the operation was successful. Returns True if a ball was successfully placed,
            and False if the operation failed (for example, if the desired position is not valid, the agent does not have a ball, or there is no hole at the position).
        """
        if not self.is_valid_position(position):
            return False
        if not agent.has_ball:
            return False
        current_cell_state = self.get_cell_state(position)
        if HOLE not in current_cell_state:
            return False

        x, y = position
        self.grid[y][x] = current_cell_state.replace(HOLE, FILLED_HOLE)
        self.holes[(x, y)] = agent.agent_id

        # switch position of other balls
        self.switch_ball_positions()
        return True

    def throw_ball_from_hole(self, position: Tuple[int, int]) -> bool:
        """
        Steals a ball from a hole at a given position in the playground and put the ball in a random empty position.

        Args:
            position: A tuple containing two integers representing row and column indices.

        Returns:
            A boolean value indicating whether the operation was successful. Returns True if a ball was successfully stolen,
            and False if the operation failed (for example, if the desired position is not valid, the agent does not have a ball, or there is no hole at the position).
        """
        if not self.is_valid_position(position):
            return False
        current_cell_state = self.get_cell_state(position)
        if FILLED_HOLE not in current_cell_state:
            return False

        # change filled hole to hole
        x, y = position
        self.grid[y][x] = current_cell_state.replace(FILLED_HOLE, HOLE)
        self.holes[(x, y)] = ''
        # put ball in a random position
        ball_position = self.get_random_empty_position()
        x, y = ball_position
        self.grid[y][x] = BALL
        self.ball_positions.add(ball_position)

        return True

    def is_valid_position(self, position: Tuple[int, int]) -> bool:
        """
        Checks if a given position is valid in the playground.

        Args:
            position: A tuple containing two integers representing row and column indices.

        Returns:
            A boolean value indicating whether the position is valid. Returns True if the position is within the grid boundaries,
            and False otherwise.
        """

        if not position:
            return False
        # Check if position is within grid boundaries
        x, y = position
        if x < 0 or x >= self.xAxis:
            return False
        if y < 0 or y >= self.xAxis:
            return False
        # (check if position is an obstacle)?
        return True

    def is_a_ball_cell(self, position: Tuple[int, int]) -> bool:
        """
        Checks if a given position in the playground is a ball cell.

        Args:
            position: A tuple containing two integers representing row and column indices.

        Returns:
            A boolean value indicating whether the position is a ball cell. Returns True if the position contains a ball,
            and False otherwise.
        """
        return BALL in self.get_cell_state(position)

    def is_a_hole_cell(self, position: Tuple[int, int]) -> bool:
        """
        Checks if a given position in the playground is a hole cell.

        Args:
            position: A tuple containing two integers representing row and column indices.

        Returns:
            A boolean value indicating whether the position is a hole cell. Returns True if the position contains a hole,
            and False otherwise.
        """
        return HOLE in self.get_cell_state(position)

    def get_full_map_for_agent(self, agent: 'Agent'):

        """
        Returns the full map for the agent, based on the agent's memory rather than the actual state of the playground.
        This includes the agent's view of balls, holes, filled holes, and the positions of friends.

        Args:
            agent: The Agent object for which the map is generated.

        Returns:
            A list of lists representing the full map for the agent, based on its memory.
        """
        map_ = [[EMPTY for _ in range(self.xAxis)] for _ in range(self.yAxis)]

        # Mark balls as per the agent's memory
        for ball_pos in agent.ball_positions:
            map_[ball_pos[1]][ball_pos[0]] = BALL

        # Mark holes as per the agent's memory
        for hole_pos in agent.hole_positions:
            map_[hole_pos[1]][hole_pos[0]] = HOLE

        # Mark filled holes as per the agent's memory
        for filled_hole_pos in agent.filled_hole_positions:
            map_[filled_hole_pos[1]][filled_hole_pos[0]] = FILLED_HOLE

        # Mark the agent's position
        map_[agent.position[1]][agent.position[0]] = agent.get_label() if map_[agent.position[1]][agent.position[0]] == EMPTY else agent.get_label() + ',' + map_[agent.position[1]][agent.position[0]]

        # Mark the positions of friends
        for friend in agent.friends:
            if (friend.position[0] < self.xAxis) and (friend.position[1] < self.yAxis):
                map_[friend.position[1]][friend.position[0]] = friend.get_label() if map_[friend.position[1]][friend.position[0]] == EMPTY else friend.get_label() + ',' + map_[friend.position[1]][friend.position[0]]

        return map_
