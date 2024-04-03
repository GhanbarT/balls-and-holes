import argparse
from Controller import Controller
from Playground import Playground
from utils import clear_screen, get_key_action
from bcolors import GREEN_HIGHLIGHT, ENDC, RED_HIGHLIGHT


def print_guid(last_index=False) -> None:
    prev_str = "\n[<--]/[a]/[A]: Previous step"
    next_str = "" if last_index else "\n[-->]/[d]/[D]: Next step"
    exit_str = "\n" + ("[⏎]/[Enter]/" if last_index else "") + "[Ctrl+C]: Exit"
    print("\n" + prev_str + next_str + exit_str)

    if last_index:
        success_message = GREEN_HIGHLIGHT + "Agent completed the task successfully" + ENDC
        failure_message = RED_HIGHLIGHT + "Agent failed the task successfully" + ENDC
        if current_agent.get_score() == controller.get_max_score():
            print(success_message)
        else:
            print(failure_message)


def v1(current_agent):
    clear_screen()
    controller.plot(legends=True).print_info()
    input()
    while current_agent.battery >= 0 and current_agent.get_score() < controller.get_max_score():
        clear_screen()
        controller.perceive_agents().next_round().plot(legends=True).print_info()
        input()

    success_message = GREEN_HIGHLIGHT + "Agent completed the task successfully" + ENDC
    failure_message = RED_HIGHLIGHT + "Agent failed the task successfully" + ENDC
    if current_agent.get_score() == controller.get_max_score():
        print(success_message)
    else:
        print(failure_message)


def v2(current_agent):
    # Run the agent until it runs out of battery or reaches the max score
    while current_agent.battery >= 0 and current_agent.get_score() < controller.get_max_score():
        controller.perceive_agents().next_round()

    # Display the results
    clear_screen()
    controller.draw_current(legends=True, info=True)
    print_guid()
    while True:
        action = get_key_action()
        if action == 'enter' and controller.is_max_draw_index():
            break
        if action == 'next':
            clear_screen()
            controller.draw_next(legends=True, info=True)
            print_guid(controller.is_max_draw_index())
        if action == 'previous':
            clear_screen()
            controller.draw_previous(legends=True, info=True)
            print_guid(controller.is_max_draw_index())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Playground parameters')
    parser.add_argument('-dim', type=str, default='5,5', help='Dimensions of the playground (default: 5,5)')
    parser.add_argument('-orb', type=int, default=5, help='Number of orbs in the playground (default: 5)')
    parser.add_argument('-hole', type=int, default=5, help='Number of holes in the playground (default: 5)')
    args = parser.parse_args()

    dim_x, dim_y = map(int, args.dim.split(','))
    dimensions: tuple[int, int] = (dim_x, dim_y)

    playground = Playground(dimension=dimensions, num_orbs=args.orb, num_holes=args.hole)
    controller = Controller(playground)
    current_agent = controller.create_agent()
    if not current_agent:
        raise ValueError("Agent was not created")

    controller.start()
    v2(current_agent)
