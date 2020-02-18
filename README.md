# Beta Knuff - Experimental Ludo (Fia med knuff) Engine written in Python 3
This project implements a custom command-line based Ludo Engine (known as *Fia med knuff* in Swedish), allowing for simulation of a large number of games, development of artifical agents and other various Ludo testing. The end goal is to implement a machine learning based agent and investigate the nature of optimal Ludo play. It implements common rule variations such as entry with two players on roll 6 and more. Recommended to be run using PyPy3 to improve simulation speed.

## Usage  
In order to start the engine, run run.py, preferably with something like PyPy to improve speed.  
For a full list of commands, enter `help` in the engine.

**Usage examples of selfplay**:  
Selfplay of four Random agents: `play random`  
Display the board throughout the selfplay: `play random -d`  
Multiple (count) games of selfplay: `play random -c [COUNT]`  
Selfplay of RuleBased, Random x3: `play rulebased random`  
Selfplay of Rulebased, Random: `play rulebased random -p 2`  
Rotate the player starting position between games to give a fairer end result: `play randomtake -c 100 -swap`  

**Implemented Player types (agents):** 
* Human - takes human input to decide move. flag -d recommended to be able to see board.
* Random - does random moves
* RandomTake - takes pieces if possible, otherwise does a random move
* RuleBased - Simple rulebased player.
* MinMax - Rulebased player doing a MinMax search.
