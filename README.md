# Balls, Holes and Agents: Multi-agent System Course Project

## Description ⚾️🕳️🤖⛳️

This project is a python game simulation where agents interact with their environment. Agents can pick up orbs, fill
holes, and
interact with other agents. The game is played in rounds, and agents can perceive their surroundings, make decisions,
and take actions based on their perceptions.

## Installation 🛠️

This project does not require any specific installation steps (just have Python installed on the system). You can clone the repository using one of the following
methods:

1. **HTTPS**: `git clone https://github.com/GhanbarT/balls-and-holes.git`
2. **SSH**: `git clone git@github.com:GhanbarT/balls-and-holes.git`
3. **GitHub CLI**: `gh repo clone GhanbarT/balls-and-holes`

After cloning the repository, navigate to the project directory:

```bash
cd ball-and-hole
```

## Usage 🕹️

To run the game simulation, use the following command:

`python main.py [arguments]`

The available command-line arguments are:

- `-dim`: Dimensions of the playground (default: '7,7')
- `-ball`: Number of balls in the playground (default: 5)
- `-hole`: Number of holes in the playground (default: 5)
- `-legends`: Show legends (default: False)
- `-info`: Show Agents' info (default: False)
- `-agents`: Agents' positions and types (default: None). Format: `<x,y,type;x,y,type;...>`. Example: `0,0,1;6,4,2`
- `-log`: Log file name (default: None)
- `-seed`: Seed for the random number generator if you want to retry a run (default: None)

Example usage  :

`python main.py -dim 10,10 -ball 10 -hole 10 -legends -info -agents 0,0,1;9,9,2 -log game.log -seed 12345`

## Project Structure 🏗️

This project is organized into several modules:

- `main.py`: This is the entry point of the application. It parses command-line arguments, sets up the game environment, and starts the game simulation.

- `controller.py`: This module contains the `Controller` class, which manages the game simulation. It handles the game rounds, agent actions, and game state.

- `playground.py`: This module defines the `Playground` class, which represents the game environment. It includes the dimensions of the playground, the number of orbs and holes, and the positions of the agents.

- `agent.py`: This module defines the `Agent` class, which represents an agent in the game. Each agent has a position, a direction, a field of view, and can interact with the environment by picking up orbs and filling holes. Agents can also communicate with each other to share information about the environment.

- `utils.py`: This module contains utility functions used throughout the project, such as `get_key_action` which is used to get the user's input for navigating through the game rounds.

- `bcolors.py`: This module defines color codes for console output, which are used to enhance the visualization of the game state in the console.

- `random_seed.py`: This module contains the `RandomSeed` class, which is used to set a seed for the random number generator. This allows for reproducible game simulations.

Please note that this is a high-level overview of the project structure. For detailed information about each module and its contents, please refer to the source code.
## Contributing 🤝

Contributions are welcome. Please fork the repository and create a pull request with your changes.

## Note 📝

All content in this README file was AI generated.