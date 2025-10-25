Tkinter Mario-Style Platformer

This is a classic platformer game, inspired by Super Mario Bros., built entirely in Python using the standard tkinter library. All graphics are drawn procedurally using the Tkinter canvas, meaning no external images or assets are required!

It serves as a demonstration of how to build a complete game with physics, collisions, enemies, and power-ups using only standard Python libraries.

(After you run the program, take a screenshot, upload it to your repository, and replace this text with the image link)

🚀 Features

Platformer Physics: Includes running (with friction), jumping, and gravity.

Enemies: Goombas with basic AI that walk, fall off ledges, and turn around.

Combat System:

Stomp on enemies to defeat them.

Get hit by an enemy to take damage.

Power-Ups:

Mushroom: Transforms Mario from "small" to "big".

Fire Flower: Transforms Mario to "fire" mode, allowing him to shoot fireballs.

Fireball Shooting: As Fire Mario, press 'X' to shoot bouncing fireballs that can defeat enemies.

Dynamic Objects: Collect spinning coins for points.

Progressive Difficulty: The game is endless, spawning new enemies, coins, and power-ups over time as the level increases.

Real-time UI: Displays your score, level, and current power-up state.

💻 How to Run

This project uses only Python's built-in libraries (tkinter, random, math). No external packages are needed.

Clone the repository:

git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
cd YOUR_REPOSITORY_NAME


Ensure you have Python 3 with Tkinter: Tkinter is included with most Python 3 installations. If you don't have it, you may need to install it:

# On Debian/Ubuntu
sudo apt-get install python3-tk

# On Fedora
sudo dnf install python3-tkinter


Run the script:

python mario_game.py


🎮 Controls

Move Left: ← (Left Arrow)

Move Right: → (Right Arrow)

Jump: Spacebar

Shoot Fireball: X (Only available in "Fire" mode)
