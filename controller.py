import random_seed
import random
from copy import deepcopy
from typing import List, Tuple, Optional, TYPE_CHECKING

import bcolors
from consts import UUID_LEN, HAVING_ORB, ORB_CELL, HOLE_CELL, FILLED_HOLE_CELL, EMPTY, OBSTACLE, ICONS, AGENT, \
    CELL_COLORS, ARROWS, HOLE, ORB, FILLED_HOLE, UP

from agent import Agent
from utils import clear_screen

if TYPE_CHECKING:
    from playground import Playground


class DrawableAgent:
    def __init__(self,
                 agent_id: str = '',
                 team: int = 1,
                 position: Tuple[int, int] = None,
                 target_position: Tuple[int, int] = None,
                 direction: str = UP,
                 has_ball: bool = False,
                 battery: int = 30,
                 score: int = 0,
                 agent: 'Agent' = None):
        if agent is not None:
            self.agent_id = agent.agent_id
            self.type = agent.type
            self.position = deepcopy(agent.position)
            self.target_position = deepcopy(agent.target_position)
            self.direction = deepcopy(agent.direction)
            self.has_ball = bool(agent.has_ball)
            self.battery = int(agent.battery)
            self.score = int(agent.get_my_score())
        else:
            self.agent_id = deepcopy(agent_id)
            self.type = team
            self.position = deepcopy(position)
            self.target_position = deepcopy(target_position)
            self.direction = deepcopy(direction)
            self.has_ball = bool(has_ball)
            self.battery = int(battery)
            self.score = int(score)

    def get_score(self):
        """
        Returns the score of the agent.
        """
        return self.score


class Draw:
    def __init__(self, playground: 'Playground', agents: List[DrawableAgent], iteration: int):
        self.playground = deepcopy(playground)
        self.grid = deepcopy(playground.grid)
        self.xAxis = len(self.grid[0])
        self.agents = agents
        self.iteration = iteration

    def plot(self, cls=True, legends: bool = False, info: bool = False) -> None:
        """
        Plots the current state of the game grid in the console.

        Args:
            cls (bool, optional): If True, the console screen will be cleared before the grid is printed.
                                  Default is True.
            legends (bool, optional): If True, the function will print a legend that explains what each symbol in the grid represents.
                                      Default is False.
            info (bool, optional): If True, the function will print additional information about the game state.
                                   Default is False.

        The grid is printed as a series of strings. Each cell in the grid is represented by a symbol that indicates what's in the cell.
        The symbols are obtained by calling the `get_icon` method of the `Draw` class for each cell.

        After creating the string representation of the grid, the function prints it to the console. If `legends` is True, it also prints
        the legend. If `info` is True, it calls `print_info` to print additional game info.

        Finally, the function prints a line that shows the current iteration number.
        """
        output = ['╔══' + '══╦══'.join(['═'] * self.xAxis) + '══╗']

        for i, row in enumerate(self.grid):
            if i > 0:
                output.append('╠══' + '══╬══'.join(['═'] * self.xAxis) + '══╣')
            output.append(
                '║' + '║'.join([f'{self.get_icon(factor, (j, i))}' for j, factor in enumerate(row)]) + '║')

        output.append('╚══' + '══╩══'.join(['═'] * self.xAxis) + '══╝')
        # Join all the strings in the list into a single string with a newline character between each string
        output_str = '\n'.join(output)

        if cls:
            clear_screen()

        print(output_str)

        if legends:
            print(
                f'{bcolors.LIGHT_MAGENTA_HIGHLIGHT}----Legends----{bcolors.ENDC}'
                f'\n-> {HAVING_ORB}Having Ball{bcolors.ENDC}'
                f'\n-> {ORB_CELL}on Ball Cell{bcolors.ENDC}'
                f'\n-> {HOLE_CELL}on Hole Cell{bcolors.ENDC}'
                f'\n-> {FILLED_HOLE_CELL}on Filled Hole Cell{bcolors.ENDC}')

        if info:
            self.print_info()

        print(
            f'---------- {bcolors.LIGHT_YELLOW_HIGHLIGHT}{bcolors.BLACK} Iteration: {str(self.iteration).rjust(3)} - Seed: {random_seed.RandomSeed().get_seed()} {bcolors.ENDC} ----------')

    def print_info(self) -> None:
        """
        Prints information about all agents in a tabular format.
        """
        # TODO: change the way get score of agents
        columns = [
            ("Agent ID", lambda x: x.agent_id),
            ("Team", lambda x: str(x.type)),
            ("Current Position", lambda x: str(x.position)),
            ("Target Position", lambda x: str(x.target_position)),
            ("Battery", lambda x: str(x.battery)),
            ("Ball", lambda x: "✔" if x.has_ball else ""),
            # ("Score", lambda x: str(x.get_score()))
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

    def get_icon(self, factor: str, position: tuple[int, int],
                 random_space=False) -> str:
        """
        Returns the icon corresponding to a given cell state.

        Args:
            factor: A string representing the state of a cell.
            position: cell position
            random_space: A boolean value indicating whether to add a random space before the icon.

        Returns:
            A string representing the icon for the given cell state.
        """
        if factor == EMPTY or factor == OBSTACLE:
            return ICONS[factor]

        if AGENT in factor:
            factors = factor.split(',')

            agent_id = factors[-1][len(AGENT) + 1:]
            agent = Controller.find_agent(self.agents, agent_id)
            text_color = HAVING_ORB if agent.has_ball else ''

            if len(factors) > 1:
                text_color += CELL_COLORS.get(factors[0], '')

            return text_color + ARROWS[agent.direction] + ICONS[AGENT] + agent_id[0:2] + bcolors.ENDC

        if factor == HOLE or factor == ORB:
            return ICONS[factor] + ' ' if random.choice([False, random_space]) else ' ' + ICONS[factor]

        if factor == FILLED_HOLE:
            filler_agent_id = self.playground.holes[position]
            agent = Controller.find_agent(self.agents, filler_agent_id)
            # this must not happen, but just to be sure
            if agent is None:
                return ICONS[factor] + ' ' * 2
            return ICONS[factor] + str(agent.type).ljust(2)[0:2]


class Controller:
    def __init__(self, playground: 'Playground', log_file: str = None):
        self.playground = playground
        self.agents: List[Agent] = []  # List to store all agents
        self.draws: list[Draw] = []
        self.draw_index = 0
        self.log_file = log_file

    def create_agent(self,
                     chatbot: bool,
                     agent_id: Optional[str] = None,
                     agent_type: int = 1,
                     position: Optional[Tuple[int, int]] = None,
                     field_of_view: Optional[int] = 3,
                     battery=30,) -> Optional['Agent']:
        """
        Creates a new agent and adds it to the playground.

        Args:
            chatbot: A boolean value indicating whether to use the chatbot.
            agent_id: A string representing the agent's ID. If not provided, a random UUID will be assigned.
            agent_type: An integer representing the type of the agent. Default is 1.
            position: A tuple containing two integers representing row and column indices.
                      If not provided, the agent will be placed at a random position.
            field_of_view: An integer representing the field of view. If not provided, the default field of view will be used.
            battery: An integer representing the initial battery level. If not provided, the default battery level will be used.

        Returns:
            A boolean value indicating whether the operation was successful. Returns True if the agent was created and added successfully,
            and False if the operation failed (for example, if the desired position is already occupied).
        """
        if position is None:
            position = self.playground.get_random_empty_position()

        agent = Agent(agent_id=agent_id,
                      agent_type=agent_type,
                      position=position,
                      field_of_view=field_of_view,
                      battery=battery,
                      log_file=self.log_file,
                      chatbot=chatbot)
        if self.playground.add_agent(agent):
            self.agents.append(agent)  # Add the new agent to the list of agents
            return agent

        return None

    def create_agents(self,
                      agents_str: Optional[str],
                      min_agent: int,
                      chatbot: bool = True,
                      team_ids: Optional[List[int]] = None) -> 'Controller':
        """
        Creates agents based on the provided string.

        Args:
            agents_str: A string containing agent information in the format "x,y,type;x,y,type;...".
                        If not provided, min_agent agents of each team type will be created at random positions.
            min_agent: An integer representing the minimum number of agents to create for each team.
            chatbot: A boolean value indicating whether to use the chatbot. Default is True.
            team_ids: A list of integers representing the team IDs.

        Raises:
            ValueError: If the number of agents created is less than the minimum number specified.

        Example:
            create_agents("0,0,1;1,1,2", 2, [1, 2])
            This will create two agents:
            - Agent 1 of type 1 at position (0, 0)
            - Agent 2 of type 2 at position (1, 1)

        Returns: self
        """
        if not team_ids:
            team_ids = [1]

        if agents_str:
            agents = agents_str.split(';')
            for agent in agents:
                agent_info = agent.split(',')
                if len(agent_info) == 3:
                    x, y, agent_type = map(int, agent_info)
                else:
                    x, y = map(int, agent_info)
                    agent_type = 1  # default agent type
                agent = self.create_agent(agent_type=agent_type, position=(x, y), chatbot=chatbot)
                if not agent:
                    raise ValueError(f"Agent at position ({x}, {y}) was not created")

        for team_id in team_ids:
            agent_counts = len(self.get_agents_by_type(team_id))
            if agent_counts < min_agent:
                # Create at least min_agent agents of each team type if no agents are specified
                for i in range(min_agent - agent_counts):
                    agent = self.create_agent(agent_type=team_id, chatbot=chatbot)
                    if not agent:
                        raise ValueError(f"Agent {agent_counts + i + 1} from team {team_id} was not created")

        return self

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

    def get_agents_by_type(self, agent_type: int) -> List[Agent]:
        """
        Returns a list of agents of the specified type.

        Args:
            agent_type: An integer representing the agent type.

        Returns:
            A list of Agent objects of the specified type.
        """
        return [agent for agent in self.agents if agent.type == agent_type]

    @staticmethod
    def find_agent(agents: List[Agent] | List['DrawableAgent'], agent_id: str) -> Optional[Agent]:
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

    def introduce_friends(self) -> 'Controller':
        """
        Introduce friends to each agent

        Returns:
            self: Returns the Controller instance.
        """
        for agent in self.agents:
            agent.add_friends(self.get_agents_by_type(agent.type))

        return self

    def start(self) -> 'Controller':
        """
        Starts the game by placing holes and orbs, and creating a new draw object.
        """
        if self.log_file:
            with open(self.log_file, 'w'):
                pass

        self.playground.place_holes_and_orbs()
        self.introduce_friends()

        self.draws.append(
            Draw(playground=self.playground,
                 agents=[DrawableAgent(agent=agent) for agent in self.agents],
                 iteration=len(self.draws),
                 ))
        return self

    # deprecated
    def perceive_agent(self, agent: Agent) -> None:
        """
        Updates the agent's perception of its surroundings.

        Args:
            agent: The Agent object to update.
        """
        surrounding_cells = self.playground.get_surrounding_cells(position=agent.position,
                                                                  field_of_view=agent.field_of_view)
        agent.see(surrounding_cells)

    # deprecated
    def perceive_agents(self) -> 'Controller':
        """
        Updates all agents' perceptions of their surroundings.

        Returns:
            self: Returns the Controller instance.
        """
        for agent in self.agents:
            self.perceive_agent(agent)

        return self

    def next_round(self) -> 'Controller':
        """
        Advances the game by one round, allowing each agent to take an action.

        Returns:
            self: Returns the Controller instance.
        """
        for agent in self.agents:
            if agent.battery < 0:
                continue
            # If agents must perceive info simultaneously; In that case, we should use old and deprecated functions.
            # In the current state, each agent is perceived of the information after the moves of the previous agents.
            surrounding_cells = self.playground.get_surrounding_cells(position=agent.position,
                                                                      field_of_view=agent.field_of_view)

            # find opposite agent of the current agent
            opposite_agent = None
            if agent.is_agent_in_front():
                vis_x, vis_y = agent.get_front_cell_indices()
                opposite_agent = [other_agent for other_agent in self.agents if
                                  other_agent.get_label() in agent.visibility[vis_y][vis_x]][0]
                if agent.log_file:
                    agent.log_collision(opposite_agent)

            agent.see(surrounding_cells).action(self.playground, opposite_agent)

        # Create a new draw object
        self.draws.append(
            Draw(playground=self.playground,
                 agents=[DrawableAgent(agent=agent) for agent in self.agents],
                 iteration=len(self.draws),
                 ))
        return self

    def draw_current(self, cls=True, legends=False, info=False) -> 'Controller':
        """
        Draws the current state of the game.

        Args:
            cls (bool, optional): If True, the console screen will be cleared before the grid is printed.
                                  Default is True.
            legends (bool, optional): If True, legends will be included in the plot. Default is False.
            info (bool, optional): If True, additional game information will be printed. Default is False.

        Returns:
            self: Returns the Controller instance.
        """
        self.draws[self.draw_index].plot(cls=cls, legends=legends, info=info)

        return self

    def draw_next(self, cls=True, legends=False, info=False) -> 'Controller':
        """
        Advances to the next state of the game and draws it.

        Args:
            cls (bool, optional): If True, the console screen will be cleared before the grid is printed.
                                  Default is True.
            legends (bool, optional): If True, legends will be included in the plot. Default is False.
            info (bool, optional): If True, additional game information will be printed. Default is False.

        Returns:
            self: Returns the Controller instance.
        """
        self.draw_index += 1
        self.draw_index = min(self.draw_index, len(self.draws) - 1)
        self.draws[self.draw_index].plot(cls=cls, legends=legends, info=info)

        return self

    def draw_previous(self, cls=True, legends=False, info=False) -> 'Controller':
        """
        Goes back to the previous state of the game and draws it.

        Args:
            cls (bool, optional): If True, the console screen will be cleared before the grid is printed.
                                  Default is True.
            legends (bool, optional): If True, legends will be included in the plot. Default is False.
            info (bool, optional): If True, additional game information will be printed. Default is False.

        Returns:
            self: Returns the Controller instance.
        """
        self.draw_index -= 1
        self.draw_index = max(0, self.draw_index)
        self.draws[self.draw_index].plot(cls=cls, legends=legends, info=info)

        return self

    def plot(self, cls=True, legends=False, info=False) -> 'Controller':
        """
        Plots the latest state of the game.

        Args:
            cls (bool, optional): If True, the console screen will be cleared before the grid is printed.
                                  Default is True.
            legends (bool, optional): If True, legends will be included in the plot. Default is False.
            info (bool, optional): If True, additional game information will be printed. Default is False.

        Returns:
            self: Returns the Controller instance.
        """
        self.draws[-1].plot(cls=cls, legends=legends)
        if info:
            self.draws[-1].print_info()

        return self

    def get_max_score(self) -> int:
        """
        Calculates the maximum possible score in the game.

        Returns:
            int: The maximum possible score, which is the minimum of the number of holes and orbs in the playground.
        """
        return min(self.playground.num_holes, self.playground.num_orbs)

    def is_last_draw_index(self) -> bool:
        """
        Checks if the current draw index is the last one.

        Returns:
            bool: True if the current draw index is the last one, False otherwise.
        """
        return self.draw_index == len(self.draws) - 1

    def agents_reached_max_score(self, agent_type: int = 1) -> bool:
        """
        Checks if all agents of the specified type have reached the maximum score.

        Args:
            agent_type: An integer representing the agent type.

        Returns:
            bool: True if all agents of the specified type have reached the maximum score, False otherwise.
        """
        return self.get_agents_by_type(agent_type)[0].get_all_agents_score() == self.get_max_score()

    def game_over(self, agent_type: int = 1) -> bool:
        """
        Checks if the game is over for the specified agent type.

        Args:
            agent_type: An integer representing the agent type.

        Returns:
            bool: True if the game is over for the specified agent type, False otherwise.
        """
        # TODO: change the end game condition
        return self.agents_reached_max_score() or all(
            agent.battery < 0 for agent in self.get_agents_by_type(agent_type))
