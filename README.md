# Beta Knuff - Experimental Ludo (Fia med knuff) Engine written in Python 3
This project implements a custom command-line based Ludo Engine (known as *Fia med knuff* in Swedish), allowing for simulation of a large number of games, development of player agents and other various Ludo testing. The end goal is to implement a machine learning based agent and investigate the nature of optimal Ludo play. It implements common rule variations such as entry with two players on roll 6 and more.

## Usage  
In order to start the engine, run run.py.
For a full list of commands, enter `help` in the engine.

**Usage examples of selfplay**:  
Selfplay of four Random agents: `play random`  
Display the board throughout the selfplay: `play random -d`  
Multiple (count) games of selfplay: `play random -c [COUNT]`  
Selfplay of RuleBased, Random x3: `play rulebased random`  
Selfplay of Rulebased, Random: `play rulebased random -p 2`  
Rotate the player starting position between games to give a fairer end result: `play randomtake -c 100 -swap`  
Use multithreading to improve simulation performance: `play r -c 1000000 -mt`  

**Implemented Player types (agents):** 
* **Human** - takes human input to decide move. flag -d recommended to be able to see board.
* **Random** - does random moves
* **RandomTake** - takes pieces if possible, otherwise does a random move
* **FirstMove** - does the first move, generally prefers moving the pieces on the board.
* **RuleBased** - simple rulebased player.
* **NormRuleBased** - similar to RuleBased, but uses a normalized score.
* **MinMax** - uses ExpectiMinMax search with the rulebased player as evaluation.
* **MonteCarlo** - uses a Monte Carlo Tree search with the rulebased player as evaluation. 
* **MLPlayer** - uses a Machine Learning model to evaluate the best move.

## Dependencies
Tested using Python 3.6.9.  
These dependencies are used for the machine-learning based players.
These players can be disabled in the config.py file, which allows the program to run without these dependencies. 
This also allows the program to be run with PyPy3, which gives a large speedup for certain player agents.  
**Tensorflow** - Machine learning library  
**Keras** - High level Tensorflow interface  
**Scikit-learn** - Used for various math functions related to ML

## Build instructions  
1. Install the required dependencies using pip: `python3 -m pip install -r requirements.txt`
2. You can now run the program with `src/run.py`