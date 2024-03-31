from typing import List, Tuple, Optional, TYPE_CHECKING

from consts import UUID_LEN

from Agent import Agent

if TYPE_CHECKING:
    from Playground import Playground


class Controller:
    def __init__(self, playground: 'Playground'):
        self.playground = playground
        self.agents: List[Agent] = []  # List to store all agents

    def create_agent(self,
                     agent_id: Optional[str] = None,
                     position: Optional[Tuple[int, int]] = (0, 0),
                     field_of_view: Optional[int] = 3) -> Optional['Agent']:
        """
        Creates a new agent and adds it to the playground.

        Args:
            agent_id: A string representing the agent's ID. If not provided, a random UUID will be assigned.
            position: A tuple containing two integers representing row and column indices.
                      If not provided, the agent will be placed at the default position (0, 0).
            field_of_view: An integer representing the field of view. If not provided, the default field of view will be used.

        Returns:
            A boolean value indicating whether the operation was successful. Returns True if the agent was created and added successfully,
            and False if the operation failed (for example, if the desired position is already occupied).
        """
        agent = Agent(agent_id=agent_id, position=position, field_of_view=field_of_view)
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

    def perceive_agent(self, agent: Agent) -> None:
        """
        Updates the agent's perception of its surroundings.

        Args:
            agent: The Agent object to update.
        """
        surrounding_cells = self.playground.get_surrounding_cells(position=agent.position,
                                                                  field_of_view=agent.field_of_view)
        agent.see(surrounding_cells)

    def perceive_agents(self) -> None:
        """
        Updates all agents' perceptions of their surroundings.
        """
        for agent in self.agents:
            self.perceive_agent(agent)

    def next_round(self) -> None:
        """
        Advances the game by one round, allowing each agent to take an action.
        """
        # Due to the fact that we will have only one agent at the moment, we do not have priority in performing the operation
        for agent in self.agents:
            agent.action(self.playground)

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
