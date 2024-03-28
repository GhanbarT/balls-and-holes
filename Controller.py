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
                     field_of_view: Optional[int] = 3) -> bool:
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
            return True

        return False

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
        surrounding_cells = self.playground.get_surrounding_cells(position=agent.position,
                                                                  field_of_view=agent.field_of_view)
        agent.see(surrounding_cells)

    def perceive_agents(self) -> None:
        for agent in self.agents:
            self.perceive_agent(agent)

    def next_round(self) -> None:
        # Due to the fact that we will have only one agent at the moment, we do not have priority in performing the operation
        for agent in self.agents:
            agent.action(self.playground)

    def print_info(self) -> None:
        print('╔═' + '═' * UUID_LEN + ('═╦═' + '═' * 16) * 2 + '═╗')
        print('║ Agent ID ' + ' ' * (UUID_LEN - len('Agent ID')) + '║' + 'Current Position' + ' ' * (18 - len('Current Position')) + '║' + 'Target Position' + ' ' * (18 - len('Target Position')) + '║')
        print('╠═' + '═' * UUID_LEN + ('═╬═' + '═' * 16) * 2 + '═╣')

        for i, agent in enumerate(self.agents):
            if i > 0:
                print('╠═' + '═' * UUID_LEN + ('═╬═' + '═' * 16) * 2 + '═╣')
            print('║ ' + f'{agent.agent_id} ║ {agent.position}  ║ {agent.target_position}' + ' ║')

        print('╚═' + '═' * UUID_LEN + ('═╩═' + '═' * 16) * 2 + '═╝')
