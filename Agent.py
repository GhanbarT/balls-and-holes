import random
from typing import Tuple, Optional, TYPE_CHECKING
import uuid

from consts import UP, RIGHT, DOWN, LEFT, AGENT, EMPTY, ORB, HOLE

if TYPE_CHECKING:
    from Playground import Playground


class Agent:
    directions = (UP, RIGHT, DOWN, LEFT)

    def __init__(self,
                 agent_id: Optional[str] = None,
                 position: Tuple[int, int] = (0, 0),
                 field_of_view: int = 3,
                 visibility: list[list[str]] = None):
        self.agent_id = agent_id if agent_id is not None \
            else str(uuid.uuid4())  # Assign a random UUID if no ID is provided
        self.position = position
        self.field_of_view = field_of_view

        self.visibility = visibility if visibility is not None \
            else [[EMPTY] * field_of_view for _ in range(field_of_view)]
        self.visibility[field_of_view // 2][field_of_view // 2] = self.get_label()

        # initial direction, battery, has_ball
        self.direction = 'up'  # Initial direction (up, down, left, right)
        self.battery = 30
        self.has_ball = False
        self.hole_positions: list[Tuple[int, int]] = list()
        self.orb_positions: list[Tuple[int, int]] = list()
        self.target_position: Optional[Tuple[int, int]] = None
        self.current_target_hole_position: Optional[Tuple[int, int]] = None
        self.current_target_orb_position: Optional[Tuple[int, int]] = None

    def turn_clockwise(self) -> str:
        current_index = self.directions.index(self.direction)
        new_index = (current_index + 1) % len(self.directions)
        self.direction = self.directions[new_index]
        return self.direction

    def take_step_forward(self, environment: 'Playground') -> bool:
        self.battery -= 1
        x, y = self.position

        new_position = None
        if self.direction == UP:
            new_position = (x, y - 1)
        elif self.direction == RIGHT:
            new_position = (x + 1, y)
        elif self.direction == DOWN:
            new_position = (x, y + 1)
        elif self.direction == LEFT:
            new_position = (x - 1, y)

        if environment.agent_enter_cell(new_position, self):
            self.position = new_position
        # Implement step forward logic (e.g., update position)
        # You can adjust the position based on the current direction

        return True

    def take_ball(self, environment: 'Playground') -> bool:
        """
        Returns:
            If the agent succeeds in picking up the ball from the ground, True; otherwise: false
        """
        self.target_position = None
        if self.has_ball:
            return False



        self.has_ball = True
        return True

    def put_ball_in_hole(self):
        self.has_ball = False
        self.target_position = None
        # Implement logic to put the ball in the hole
        # You can adjust the position based on the current direction

    def see(self, visibility: list[list[str]]) -> None:
        self.visibility = visibility

    def update_item_positions(self) -> None:
        # Calculate the top-left position of the visibility grid in the playground
        top_left_x = self.position[0] - self.field_of_view // 2
        top_left_y = self.position[1] - self.field_of_view // 2

        print(self.visibility)
        # Iterate over each cell in the visibility grid
        for i in range(len(self.visibility)):
            for j in range(len(self.visibility[i])):
                # Calculate the actual position of the cell in the playground
                env_x, env_y = top_left_x + j, top_left_y + i
                if ORB in self.visibility[i][j] and (env_x, env_y) not in self.orb_positions:
                    self.orb_positions.append((env_x, env_y))
                if HOLE in self.visibility[i][j] and (env_x, env_y) not in self.hole_positions:
                    self.hole_positions.append((env_x, env_y))

    def update_target(self, environment: 'Playground') -> None:
        if self.target_position is not None:
            return

        target_list = self.hole_positions if self.has_ball else self.orb_positions

        if len(target_list) > 0:
            self.target_position = self.find_nearest_target(target_list)
        else:
            self.target_position = self.find_random_position(environment)

    def find_nearest_target(self, target_list: list[Tuple[int, int]]) -> Tuple[int, int]:
        nearest_target = min(target_list, key=lambda pos: AGENT.manhattan_distance(self.position, pos))
        target_list.remove(nearest_target)
        return nearest_target

    def find_random_position(self, environment: 'Playground') -> Tuple[int, int]:
        while True:
            random_position = (random.randint(0, self.field_of_view - 1), random.randint(0, self.field_of_view - 1))
            if random_position not in environment.agent_start_positions:
                return random_position

    def action(self, environment: 'Playground'):
        self.update_item_positions()
        if self.target_position == self.position:
            if self.has_ball:
                self.put_ball_in_hole()
                return
            else:
                self.take_ball(environment)
                return

        self.update_target(environment)

        target_x, target_y = self.target_position
        if self.position[0] < target_x:
            while self.direction != RIGHT:
                self.turn_clockwise()
        elif self.position[0] > target_x:
            while self.direction != LEFT:
                self.turn_clockwise()
        elif self.position[1] < target_y:
            while self.direction != DOWN:
                self.turn_clockwise()
        elif self.position[1] > target_y:
            while self.direction != UP:
                self.turn_clockwise()
        self.take_step_forward(environment)

    def get_label(self) -> str:
        return AGENT + '-' + self.agent_id

    @staticmethod
    def manhattan_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
