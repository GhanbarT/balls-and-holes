import random
from copy import deepcopy
from typing import List, Tuple, Optional, TYPE_CHECKING

import bcolors
from consts import UUID_LEN, HAVING_ORB, ORB_CELL, HOLE_CELL, FILLED_HOLE_CELL, EMPTY, OBSTACLE, ICONS, AGENT, \
    CELL_COLORS, ARROWS, HOLE, ORB, FILLED_HOLE

from Agent import Agent

if TYPE_CHECKING:
    from Playground import Playground


class DrawableAgent:
    def __init__(self,
                 agent_id: str = None,
                 position: Tuple[int, int] = None,
                 target_position: Tuple[int, int] = None,
                 direction: str = None,
                 has_ball: bool = False,
                 battery: int = 30,
                 score: int = 0,
                 agent: 'Agent' = None):
        if agent is not None:
            self.agent_id = deepcopy(agent.agent_id)
            self.position = deepcopy(agent.position)
            self.target_position = deepcopy(agent.target_position)
            self.direction = deepcopy(agent.direction)
            self.has_ball = deepcopy(agent.has_ball)
            self.battery = deepcopy(agent.battery)
            self.score = deepcopy(agent.get_score())
        else:
            self.agent_id = deepcopy(agent_id)
            self.position = deepcopy(position)
            self.target_position = deepcopy(target_position)
            self.direction = deepcopy(direction)
            self.has_ball = deepcopy(has_ball)
            self.battery = deepcopy(battery)
            self.score = deepcopy(score)

    def get_score(self):
        return self.score


class Draw:
    def __init__(self, grid: list[list[str]], agents: List[DrawableAgent], iteration: int):
        self.grid = deepcopy(grid)
        self.xAxis = len(grid[0])
        self.agents = agents
        self.iteration = iteration

    def plot(self, legends: bool = False, info: bool = False) -> None:
        output = ['╔══' + '══╦══'.join(['═'] * self.xAxis) + '══╗']

        for i, row in enumerate(self.grid):
            if i > 0:
                output.append('╠══' + '══╬══'.join(['═'] * self.xAxis) + '══╣')
            output.append('║' + '║'.join([f'{Draw.get_icon(self.agents, factor)}' for factor in row]) + '║')

        output.append('╚══' + '══╩══'.join(['═'] * self.xAxis) + '══╝')

        # Join all the strings in the list into a single string with a newline character between each string
        output_str = '\n'.join(output)

        print(output_str)
        if legends:
            print(
                f'----Legends----'
                f'\n-> {HAVING_ORB}Having Orb{bcolors.ENDC}'
                f'\n-> {ORB_CELL}on Orb Cell{bcolors.ENDC}'
                f'\n-> {HOLE_CELL}on Hole Cell{bcolors.ENDC}'
                f'\n-> {FILLED_HOLE_CELL}on Filled Hole Cell{bcolors.ENDC}')

        if info:
            self.print_info()

        print(
            f'------------------------------------- Iteration: {str(self.iteration).rjust(3)} -------------------------------------')

    def print_info(self) -> None:
        """
        Prints information about all agents in a tabular format.
        """
        columns = [
            ("Agent ID", lambda x: x.agent_id),
            ("Current Position", lambda x: str(x.position)),
            ("Target Position", lambda x: str(x.target_position)),
            ("Battery", lambda x: str(x.battery)),
            ("Ball", lambda x: "✔" if x.has_ball else ""),
            ("Score", lambda x: str(x.get_score()))
        ]
        column_widths = [UUID_LEN] + [len(title) for title, _ in columns[1:]]

        # Print the top border
        print('┌' + '┬'.join('─' * width for width in column_widths) + '┐')
        # Print the column titles
        print('│' + '│'.join(f"{title.ljust(width)}" for (title, _), width in zip(columns, column_widths)) + '│')
        # Print the separator line
        print('├' + '┼'.join('─' * width for width in column_widths) + '┤')

        # Print the values for each agent
        for i, agent in enumerate(self.agents):
            if i > 0:
                print('├' + '┼'.join('─' * width for width in column_widths) + '┤')
            print('│' + '│'.join(
                f"{value_func(agent).ljust(width)}" for (_, value_func), width in zip(columns, column_widths)) + '│')

        # Print the bottom border
        print('└' + '┴'.join('─' * width for width in column_widths) + '┘')

    @staticmethod
    def get_icon(agents: List['Agent'] | List['DrawableAgent'], factor: str, random_space=False) -> str:
        """
        Returns the icon corresponding to a given cell state.

        Args:
            agents: A list of Agent objects.
            factor: A string representing the state of a cell.
            random_space: A boolean value indicating whether to add a random space before the icon.

        Returns:
            A string representing the icon for the given cell state.
        """
        if factor == EMPTY or factor == OBSTACLE:
            return ICONS[factor]

        if AGENT in factor:
            factors = factor.split(',')

            # FIXME: fix AGENT and other factors generally
            agent_id = factors[-1][len(AGENT) + 1:]
            agent = Controller.find_agent(agents, agent_id)
            text_color = HAVING_ORB if agent.has_ball else ''

            if len(factors) > 1:
                text_color += CELL_COLORS.get(factors[0], '')

            return text_color + ARROWS[agent.direction] + ICONS[AGENT] + agent_id[0:2] + bcolors.ENDC

        if factor == HOLE or factor == ORB or factor == FILLED_HOLE:
            return ICONS[factor] + ' ' if random.choice([False, random_space]) else ' ' + ICONS[factor]


class Controller:
    def __init__(self, playground: 'Playground'):
        self.playground = playground
        self.agents: List[Agent] = []  # List to store all agents
        self.draws: list[Draw] = []
        self.draw_index = 0

    def create_agent(self,
                     agent_id: Optional[str] = None,
                     position: Optional[Tuple[int, int]] = (0, 0),
                     field_of_view: Optional[int] = 3,
                     battery=30) -> Optional['Agent']:
        """
        Creates a new agent and adds it to the playground.

        Args:
            agent_id: A string representing the agent's ID. If not provided, a random UUID will be assigned.
            position: A tuple containing two integers representing row and column indices.
                      If not provided, the agent will be placed at the default position (0, 0).
            field_of_view: An integer representing the field of view. If not provided, the default field of view will be used.
            battery: An integer representing the initial battery level. If not provided, the default battery level will be used.

        Returns:
            A boolean value indicating whether the operation was successful. Returns True if the agent was created and added successfully,
            and False if the operation failed (for example, if the desired position is already occupied).
        """
        agent = Agent(agent_id=agent_id, position=position, field_of_view=field_of_view, battery=battery)
        if self.playground.add_agent(agent):
            self.agents.append(agent)  # Add the new agent to the list of agents
            return agent

        return None

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

    @staticmethod
    def find_agent(agents: List[Agent], agent_id: str) -> Optional[Agent]:
        """
        Returns the agent with the specified ID from a list of agents.

        Args:
            agents: A list of Agent objects.
            agent_id: A string representing the agent's ID.

        Returns:
            The Agent object with the specified ID, or None if no such agent exists in the provided list.
        """
        for agent in agents:
            if agent.agent_id == agent_id:
                return agent
        return None

    def start(self) -> 'Controller':
        """
        Starts the game by placing holes and orbs, and creating a new agent.
        """
        self.playground.place_holes_and_orbs()
        self.draws.append(
            Draw(grid=self.playground.grid,
                 agents=[DrawableAgent(agent=agent) for agent in self.agents],
                 iteration=len(self.draws)
                 ))
        return self

    def perceive_agent(self, agent: Agent) -> None:
        """
        Updates the agent's perception of its surroundings.

        Args:
            agent: The Agent object to update.
        """
        surrounding_cells = self.playground.get_surrounding_cells(position=agent.position,
                                                                  field_of_view=agent.field_of_view)
        agent.see(surrounding_cells)

    def perceive_agents(self) -> 'Controller':
        """
        Updates all agents' perceptions of their surroundings.
        """
        for agent in self.agents:
            self.perceive_agent(agent)

        return self

    def next_round(self) -> 'Controller':
        """
        Advances the game by one round, allowing each agent to take an action.
        """
        # Due to the fact that we will have only one agent at the moment, we do not have priority in performing the operation
        for agent in self.agents:
            agent.action(self.playground)

        # Create a new draw object
        self.draws.append(
            Draw(grid=self.playground.grid,
                 agents=[DrawableAgent(agent=agent) for agent in self.agents],
                 iteration=len(self.draws)
                 ))
        return self

    def draw_current(self, legends=False, info=False) -> 'Controller':
        self.draws[self.draw_index].plot(legends=legends, info=info)

        return self

    def draw_next(self, legends=False, info=False) -> 'Controller':
        self.draw_index += 1
        self.draw_index = min(self.draw_index, len(self.draws) - 1)
        self.draws[self.draw_index].plot(legends=legends, info=info)

        return self

    def draw_previous(self, legends=False, info=False) -> 'Controller':
        self.draw_index -= 1
        self.draw_index = max(0, self.draw_index)
        self.draws[self.draw_index].plot(legends=legends, info=info)

        return self

    def plot(self, legends=False) -> 'Controller':
        self.draws[-1].plot(legends=legends)
        return self

    def print_info(self) -> 'Controller':
        """
        Prints information about all agents in a tabular format.
        """
        self.draws[-1].print_info()
        return self

    def get_max_score(self) -> int:
        return min(self.playground.num_holes, self.playground.num_orbs)

    def is_max_draw_index(self):
        return self.draw_index == len(self.draws) - 1
