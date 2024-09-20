# Hand Interface
Experiments on interacting with programs using hand gestures, currently using [mediapipe](https://github.com/google-ai-edge/mediapipe/).
Currently only tested on Windows.

### Installation

It is highly recommended to create a python virtual environment after downloading the source
```
python -m venv venv
venv\Scripts\activate
```
After downloading the source, install the required pip packages through
```
pip install -r requirements.txt
```
And you're all set!

### Running the Program

If you created a venv, activate it with
```
venv\Scripts\activate
```
and run the program 
```
cd src
py main.py
```

When the program starts, the current terminal window gets set as "always on top", otherwise the hand detection would run at like 1/10th of the framerate when you minimize it. It's obviously not a permanent solution, but for now you can pop the window in a corner and make it as small as you can (don't minimize it!)

To start the mouse mode, write "mouse" in the terminal after the program has finished booting up.

### Current Features

##### Modes

Currently 3 modes are *somewhat* implemented, **mouse**, **gusts** and **flicks**. To switch between modes, at any time, tap your pinky and thumb together.

##### Mouse

In this mode your index finger and thumb simulate a mouse:

- **move the cursor**: the cursor is a point between your index finger and thumb, move your hand to control it.
- **left mouse button**: pinch your index finger and thumb
- **double click**: tap your middle finger and thumb
- **right mouse button**: pinch your ring finger and thumb
- **scroll**: stick out only the index and middle finger and join them, then slowly move them up and down to scroll

##### Gusts & Flicks

These modes respectively move the windows and control the "back" and "forward" commands (i.e moving through pages). I however forgot how I programmed the hand detection, so you can either check the source out or just swing your hand around a bunch and see what happens.