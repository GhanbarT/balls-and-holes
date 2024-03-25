from typing import List, Tuple, Optional, Set
from os import system, name
# from time import sleep
import random
import uuid
import bcolors

UUID_LEN = 36

HAVING_ORB = bcolors.YELLOW
ORB_CELL = bcolors.GRAY_HIGHLIGHT
HOLE_CELL = bcolors.GREEN_HIGHLIGHT

EMPTY = 'empty'
AGENT = 'agent'
HOLE = 'hole'
ORB = 'orb'
OBSTACLE = 'obstacle'
OUTSIDE = 'out'

UP = 'up'
RIGHT = 'right'
DOWN = 'down'
LEFT = 'left'

icons = {
    EMPTY: ' ' * 5,
    AGENT: '🤖',
    HOLE: ' 🕳️ ',
    ORB: ' 🪨 ',
    OBSTACLE: '█' * 5
}

arrows = {
    UP: '⮙',
    RIGHT: '⮚',
    DOWN: '⮛',
    LEFT: '⮘'
}


def clear_screen() -> None:
    # for windows
    if name == 'nt':
        _ = system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')


class Agent:
    directions = (UP, RIGHT, DOWN, LEFT)

    def __init__(self, agent_id: Optional[str] = None, position: Tuple[int, int] = (0, 0), field_of_view: int = 3):
        self.agent_id = agent_id if agent_id is not None else str(
            uuid.uuid4())  # Assign a random UUID if no ID is provided
        self.position = position
        self.field_of_view = field_of_view
        self.visibility = [[EMPTY] * field_of_view for _ in range(field_of_view)]
        self.visibility[field_of_view // 2][field_of_view // 2] = AGENT + '-' + self.agent_id

        # initial direction, battery, has_ball
        self.direction = 'up'  # Initial direction (up, down, left, right)
        self.battery = 30
        self.has_ball = False

    def turn_clockwise(self) -> str:
        current_index = self.directions.index(self.direction)
        new_index = (current_index + 1) % len(self.directions)
        self.direction = self.directions[new_index]
        return self.direction

    def take_step_forward(self):
        self.battery -= 1
        # Implement step forward logic (e.g., update position)
        # You can adjust the position based on the current direction

    def take_ball(self) -> bool:
        """
        :return: If the agent succeeds in picking up the ball from the ground, True; otherwise: false
        """
        if self.has_ball:
            return False

        self.has_ball = True
        return True

    def put_ball_in_hole(self):
        self.has_ball = False
        # Implement logic to put the ball in the hole
        # You can adjust the position based on the current direction

    def see(self, visibility: list[list[str]]) -> None:
        self.visibility = visibility


class Playground:

    def __init__(self, num_holes: int = 5, num_orbs: int = 5, field_of_view: int = 3):
        self.grid = [[EMPTY] * 5 for _ in range(5)]
        self.agent_start_positions: Set[Tuple[int, int]] = set()  # Store unique agent positions
        self.agents: List[Agent] = []  # List to store all agents
        self.num_holes = num_holes
        self.num_orbs = num_orbs
        self.field_of_view = field_of_view

    def add_agent(self, agent_id: Optional[str] = None, position: Optional[Tuple[int, int]] = None) -> None:
        """
        Adds an agent to the specified position on the grid.

        Args:
            agent_id: An integer representing the agent's ID. If not provided, a random UUID will be assigned.
            position: A list containing two integers representing row and column indices.
                      If not provided, the agent will be placed at the default position (0, 0).
        """
        if position is None:
            position = (0, 0)  # Default position
        self.agent_start_positions.add(position)  # Save the unique position

        x, y = position
        agent = Agent(agent_id=agent_id, position=position, field_of_view=self.field_of_view)
        self.agents.append(agent)  # Add the new agent to the list of agents
        self.grid[x][y] = AGENT + '-' + agent.agent_id  # Agent

    def get_agent_by_id(self, agent_id: str) -> Optional[Agent]:
        """
        Returns the agent with the specified ID.

        Args:
            agent_id: An integer representing the agent's ID.

        Returns:
            The Agent object with the specified ID, or None if no such agent exists.
        """
        for agent in self.agents:
            if agent.agent_id == agent_id:
                return agent
        return None

    def place_holes_and_orbs(self) -> None:
        """
        Randomly places holes and orbs (soil) on the grid, avoiding agent positions.

        The algorithm ensures that each position is unique and not already occupied by an agent.
        """
        available_positions = [(i, j) for i in range(5) for j in range(5) if (i, j) not in self.agent_start_positions]
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

        Args: position: A tuple containing two integers representing row and column indices. field_of_view: An
        integer representing the field of view. Value of the field of view must be an odd number; Otherwise,
        it will be considered as the smallest number greater than the desired number.

        :returns:
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

    def perceive_agent(self, agent: Agent):
        surrounding_cells = self.get_surrounding_cells(position=agent.position, field_of_view=agent.field_of_view)
        agent.see(surrounding_cells)

    def perceive_agents(self) -> None:
        for agent in self.agents:
            self.perceive_agent(agent)

    def plot(self, legends: bool = False) -> None:
        clear_screen()
        print('╔══' + '══╦══'.join(['═'] * 5) + '══╗')

        for i, row in enumerate(self.grid):
            if i > 0:
                print('╠══' + '══╬══'.join(['═'] * 5) + '══╣')
            print('║' + '║'.join([f'{self.get_icon(factor)}' for factor in row]) + '║')

        print('╚══' + '══╩══'.join(['═'] * 5) + '══╝')
        if legends:
            print(
                f'----Legends----'
                f'\n-> {HAVING_ORB}Having Orb{bcolors.ENDC}'
                f'\n-> {ORB_CELL}on Orb Cell{bcolors.ENDC}'
                f'\n-> {HOLE_CELL}on Hole Cell{bcolors.ENDC}')

    def print_info(self):
        print('╔═' + '═' * UUID_LEN + '═╦═' + '═' * 6 + '═╗')
        print('║ Agent ID ' + ' ' * (UUID_LEN - len('Agent ID')) + '║' + 'Position' + '║')
        print('╠═' + '═' * UUID_LEN + '═╬═' + '═' * 6 + '═╣')

        for i, agent in enumerate(self.agents):
            if i > 0:
                print('╠═' + '═' * UUID_LEN + '═╬═' + '═' * 6 + '═╣')
            print('║ ' + f'{agent.agent_id} ║ {agent.position}' + ' ║')

        print('╚═' + '═' * UUID_LEN + '═╩═' + '═' * 6 + '═╝')

    def get_icon(self, factor: str) -> str:
        if factor == EMPTY or factor == OBSTACLE:
            return icons[factor]

        if factor.startswith(AGENT):
            factors = factor.split(',')
            agent_id = factors[0][len(AGENT) + 1:]
            agent = self.get_agent_by_id(agent_id)
            text_color = bcolors.YELLOW if agent.has_ball else bcolors.ENDC

            if len(factors) > 1:
                text_color += bcolors.GRAY_HIGHLIGHT if factors[1] == ORB else bcolors.GREEN_HIGHLIGHT

            return text_color + arrows[agent.direction] + icons[AGENT] + agent_id[0:2] + bcolors.ENDC

        if factor == HOLE or factor == ORB:
            return icons[factor] + ' ' if random.choice([True, False]) else ' ' + icons[factor]


if __name__ == '__main__':
    playground = Playground()
    playground.add_agent()
    playground.add_agent(position=(2, 2))
    playground.place_holes_and_orbs()

    playground.agents[0].has_ball = True

    playground.agents[0].position = (1, 1)
    playground.grid[1][1] = AGENT + '-' + playground.agents[0].agent_id + (
        (',' + (ORB if playground.grid[1][1] == ORB else HOLE if playground.grid[1][1] == HOLE else '')) if
        playground.grid[1][1] != EMPTY else '')
    playground.grid[0][0] = EMPTY

    playground.plot(legends=True)
    playground.perceive_agent(agent=playground.agents[0])
    print(playground.agents[0].visibility)
    # playground.print_info()
