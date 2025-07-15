import argparse
import os

from random_seed import RandomSeed
from chatbot import Chatbot

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
        success_message = GREEN_HIGHLIGHT + "Agents completed the task successfully" + ENDC
        print(success_message)


def v1(show_legends, show_info):
    controller.plot(legends=show_legends, info=show_info)
    if not args.chatbot:
        print("\nPress [⏎]/[Enter] for next step")
        input()
    while not controller.game_over():
        controller.perceive_agents().next_round().plot(legends=show_legends, info=show_info)
        if not args.chatbot:
            print("\nPress [⏎]/[Enter] for next step")
            input()

    success_message = GREEN_HIGHLIGHT + "Agent completed the task successfully" + ENDC
    failure_message = RED_HIGHLIGHT + "Agent failed the task successfully" + ENDC
    if controller.agents_reached_max_score():
        print(success_message)
    else:
        print(failure_message)


def v2(show_legends: bool, show_info: bool):
    while not controller.game_over():
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


def parse_arguments():
    parser = argparse.ArgumentParser(description='game parameters')
    parser.add_argument('-dim', type=str, default='5,5', help='Dimensions of the playground (default: 5,5)')
    parser.add_argument('-ball', type=int, default=3, help='Number of balls in the playground (default: 3)')
    parser.add_argument('-hole', type=int, default=3, help='Number of holes in the playground (default: 3)')
    parser.add_argument('-legends', action='store_true', help='Show legends (default: False)')
    parser.add_argument('-info', action='store_true', help='Show Agents\' info (default: False)')
    parser.add_argument('-agents',
                        type=str,
                        help='Agents\' positions and types (default: None). format:<x,y,type;x,y,type;...>.example: 0,0,1;6,4,2')
    parser.add_argument('-log', type=str, help='Log file name (default: None)')
    parser.add_argument('-phased',
                        default=False,
                        action='store_true',
                        help='Use phased version of the game. In this version, it is not possible to navigate between steps (default: False)')
    parser.add_argument('-no-chatbot', dest='chatbot', default=True, action='store_false', help='dont use LLM chatbot as core')
    parser.add_argument('-model', type=int, default=6, help='Model number for the chatbot (default: 6)')
    parser.add_argument('-username', type=str, default=None, help='Username for the chatbot (default: None)')
    parser.add_argument('-password', type=str, default=None, help='Password for the chatbot (default: None)')
    parser.add_argument('-use-env-var', dest='envar', default=False, action='store_true',
                        help='Use environment variable for login(default: False)')
    parser.add_argument('-seed',
                        type=int,
                        default=None,
                        help='Seed for the random number generator if you want retry a run (default: None)')
    return parser.parse_args()


def initialize_playground_and_controller(args):
    RandomSeed().set_seed(args.seed)

    dim_x, dim_y = map(int, args.dim.split(','))
    playground = Playground(dimensions=(dim_x, dim_y), num_balls=args.ball, num_holes=args.hole)
    controller = Controller(playground=playground, log_file=args.log)
    controller.create_agents(args.agents, 1, chatbot=args.chatbot)
    controller.start()
    return controller


def configure_chatbot(args):
    if not args.chatbot:
        return
    chatbot_username = os.getenv('CHATBOT_USERNAME') if args.envar else args.username
    chatbot_password = os.getenv('CHATBOT_PASSWORD') if args.envar else args.password
    if not (chatbot_username and chatbot_password):
        raise ValueError("Error: Chatbot username or password environment variables are not set.")

    Chatbot().configure(username=chatbot_username, password=chatbot_password, model=args.model)


if __name__ == '__main__':
    args = parse_arguments()
    controller = initialize_playground_and_controller(args)

    configure_chatbot(args)

    if args.phased:
        v1(show_legends=args.legends, show_info=args.info)
    else:
        v2(show_legends=args.legends, show_info=args.info)
