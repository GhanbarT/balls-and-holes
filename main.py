import argparse
from controller import Controller
from playground import Playground
from utils import get_key_action
from bcolors import GREEN_HIGHLIGHT, ENDC, RED_HIGHLIGHT


def print_guid(last_index=False) -> None:
    prev_str = "\n[<--]/[a]/[A]: Previous step"
    next_str = "" if last_index else "\n[-->]/[d]/[D]: Next step"
    exit_str = "\n" + ("[⏎]/[Enter]/" if last_index else "") + "[Ctrl+C]: Exit"
    print("\n" + prev_str + next_str + exit_str)

    if last_index:
        success_message = GREEN_HIGHLIGHT + "Agent completed the task successfully" + ENDC
        failure_message = RED_HIGHLIGHT + "Agent failed the task successfully" + ENDC
        if controller.agents[0].get_all_agents_score() == controller.get_max_score():
            print(success_message)
        else:
            print(failure_message)


def v2(current_agent, show_legends, show_info):
    # Run the agent until it runs out of battery or reaches the max score
    # FIXME: fix the condition to stop the agent when their battery runs out
    while current_agent.battery >= 0 and current_agent.get_all_agents_score() < controller.get_max_score():
        controller.next_round()

    # Display the results
    controller.draw_current(legends=show_legends, info=show_info)
    print_guid()
    while True:
        action = get_key_action()
        if action == 'enter' and controller.is_last_draw_index():
            break
        if action == 'next':
            controller.draw_next(legends=show_legends, info=show_info)
            print_guid(controller.is_last_draw_index())
        if action == 'previous':
            controller.draw_previous(legends=show_legends, info=show_info)
            print_guid(controller.is_last_draw_index())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='game parameters')
    parser.add_argument('-dim', type=str, default='5,5', help='Dimensions of the playground (default: 5,5)')
    parser.add_argument('-ball', type=int, default=5, help='Number of balls in the playground (default: 5)')
    parser.add_argument('-hole', type=int, default=5, help='Number of holes in the playground (default: 5)')
    parser.add_argument('-legends', action='store_true', help='Show legends (default: False)')
    parser.add_argument('-info', action='store_true', help='Show Agents\' info (default: False)')
    parser.add_argument('-agents', type=str, help='Agents\' positions and types (default: None)')
    args = parser.parse_args()

    with open('output.txt', 'w'):
        pass

    dim_x, dim_y = map(int, args.dim.split(','))
    playground = Playground(dimensions=(dim_x, dim_y), num_orbs=args.ball, num_holes=args.hole)
    controller = Controller(playground)
    controller.create_agents(args.agents, 2)
    controller.start()

    v2(controller.agents[0], show_legends=args.legends, show_info=args.info)
