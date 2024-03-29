# from time import sleep
from time import sleep

from Controller import Controller
from Playground import Playground

if __name__ == '__main__':
    playground = Playground()
    controller = Controller(playground)
    controller.create_agent()
    playground.place_holes_and_orbs()

    # controller.agents[0].has_ball = True

    # playground.agents[0].position = (1, 1)
    # playground.grid[1][1] = AGENT + '-' + playground.agents[0].agent_id + (
    #     (',' + (ORB if playground.grid[1][1] == ORB else HOLE if playground.grid[1][1] == HOLE else '')) if
    #     playground.grid[1][1] != EMPTY else '')
    # playground.grid[0][0] = EMPTY
    playground.plot(agents=controller.agents, legends=True)
    controller.print_info()

    for i in range(10):
        controller.perceive_agents()
        controller.next_round()
        input()
        playground.plot(agents=controller.agents, legends=True)
        controller.print_info()

    # print(playground.agents[0].visibility)
    # playground.print_info()
