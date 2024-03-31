from Controller import Controller
from Playground import Playground
from utils import clear_screen

if __name__ == '__main__':
    hole_count = orb_count = 5
    max_score = min(hole_count, orb_count)

    playground = Playground()
    controller = Controller(playground)
    current_agent = controller.create_agent()
    if not current_agent:
        raise ValueError("Agent was not created")

    playground.place_holes_and_orbs()

    clear_screen()
    playground.plot(agents=controller.agents, legends=True)
    controller.print_info()
    input()
    while current_agent.battery >= 0 and current_agent.get_score() < max_score:
        clear_screen()
        controller.perceive_agents()
        controller.next_round()
        playground.plot(agents=controller.agents, legends=True)
        controller.print_info()
        input()

    # TODO: add history to playground and controller so that we can move between different times
    print("Agent completed the task successfully" if current_agent.get_score() == max_score else "Game Over")
