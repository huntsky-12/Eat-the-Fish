# Eat the Fish 🎣

**Eat the Fish** is a retro-inspired arcade game built in Python using the **Arcade** library. Players compete against an AI to collect the most fish on a grid-based board. The game features colorful tiles, smooth animations, and a fun competitive AI opponent.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [How to Play](#how-to-play)
- [Game Mechanics](#game-mechanics)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- Grid-based fish collection gameplay
- Player vs AI mode
- Colorful and retro arcade visuals
- Score tracking and game-over messages
- Simple and intuitive controls

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/huntsky-12/Eat-the-Fish.git
cd Eat-the-Fish
```

2. Create a virtual environment (optional but recommended):

```bash
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## How to Play

1. Run the game:

```bash
python fish_game_arcade.py
```

2. Use arrow keys or WASD to move your player.
3. Collect fish tiles to increase your score.
4. Compete against the AI to collect more fish than it.
5. The game ends when no moves are left, and the winner is displayed.

---

## Game Mechanics

- The game is played on a 2x2 or larger grid.
- Each tile contains a number of fish.
- Players take turns moving to collect fish.
- The AI makes decisions based on available moves.
- Scores are tracked in real-time, and a game-over popup shows the result.

---

## Dependencies

- Python 3.10+
- arcade
- tkinter (for popups)
- Other libraries listed in requirements.txt

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a new branch (`git checkout -b feature-name`)
3. Make your changes and commit (`git commit -m "Add feature"`)
4. Push to the branch (`git push origin feature-name`)
5. Create a pull request

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.
