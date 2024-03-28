from typing import List, Tuple, Set, TYPE_CHECKING
import random

import bcolors
from utils import clear_screen
from consts import EMPTY, HOLE, ORB, HAVING_ORB, ORB_CELL, HOLE_CELL, OBSTACLE, icons, AGENT, arrows, FILLED_HOLE

from Controller import Controller

if TYPE_CHECKING:
    from Agent import Agent


class Playground:

    def __init__(self,
                 dimension: Tuple[int, int] = (5, 5),
                 num_holes: int = 5,
                 num_orbs: int = 5,
                 field_of_view: int = 3):
        self.dimension = dimension
        self.xAxis, self.yAxis = dimension
        self.grid = [[EMPTY] * self.xAxis for _ in range(self.yAxis)]

        self.agent_start_positions: Set[Tuple[int, int]] = set()  # Store unique agent positions
        self.num_holes = num_holes
        self.num_orbs = num_orbs
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
        self.grid[x][y] = agent.get_label()

        return True

    def place_holes_and_orbs(self) -> None:
        """
        Randomly places holes and orbs (soil) on the grid, avoiding agent positions.

        The algorithm ensures that each position is unique and not already occupied by an agent.
        """
        available_positions = [(i, j) for i in range(self.yAxis) for j in range(self.xAxis) if
                               (i, j) not in self.agent_start_positions]
        random.shuffle(available_positions)

        # Place holes
        for i in range(self.num_holes):
            if len(available_positions) == 0:
                break
            x, y = available_positions.pop(0)
            self.grid[x][y] = HOLE

        # Place orbs
        for i in range(self.num_orbs):
            if len(available_positions) == 0:
                break
            x, y = available_positions.pop(0)
            self.grid[x][y] = ORB

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

        for i in range(x - field_of_view // 2, x + field_of_view // 2 + 1):
            row = []
            for j in range(y - field_of_view // 2, y + field_of_view // 2 + 1):
                if i < 0 or j < 0 or i >= len(self.grid) or j >= len(self.grid[0]):
                    row.append('out')
                else:
                    row.append(self.grid[i][j])
            surrounding_cells.append(row)

        return surrounding_cells

    def is_valid_position(self, position: Tuple[int, int]):
        # Check if position is within grid boundaries
        x, y = position
        if x < 0 or x >= self.xAxis:
            return False
        if y < 0 or y >= self.xAxis:
            return False
        # (check if position is an obstacle)?

        return True

    def plot(self, agents: List['Agent'], legends: bool = False) -> None:
        clear_screen()
        print('╔══' + '══╦══'.join(['═'] * self.xAxis) + '══╗')

        for i, row in enumerate(self.grid):
            if i > 0:
                print('╠══' + '══╬══'.join(['═'] * self.xAxis) + '══╣')
            print('║' + '║'.join([f'{self.get_icon(agents, factor)}' for factor in row]) + '║')

        print('╚══' + '══╩══'.join(['═'] * self.xAxis) + '══╝')
        if legends:
            print(
                f'----Legends----'
                f'\n-> {HAVING_ORB}Having Orb{bcolors.ENDC}'
                f'\n-> {ORB_CELL}on Orb Cell{bcolors.ENDC}'
                f'\n-> {HOLE_CELL}on Hole Cell{bcolors.ENDC}')

    @staticmethod
    def get_icon(agents: List['Agent'], factor: str) -> str:
        if factor == EMPTY or factor == OBSTACLE:
            return icons[factor]

        if factor.startswith(AGENT):
            factors = factor.split(',')
            agent_id = factors[0][len(AGENT) + 1:]
            agent = Controller.find_agent(agents, agent_id)
            text_color = bcolors.YELLOW if agent.has_ball else bcolors.ENDC

            if len(factors) > 1:
                text_color += bcolors.GRAY_HIGHLIGHT if factors[1] == ORB else bcolors.GREEN_HIGHLIGHT

            return text_color + arrows[agent.direction] + icons[AGENT] + agent_id[0:2] + bcolors.ENDC

        if factor == HOLE or factor == ORB or factor == FILLED_HOLE:
            return icons[factor] + ' ' if random.choice([True, False]) else ' ' + icons[factor]