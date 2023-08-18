# Keep heading north

This repository contains a basic prototype of a text adventure created with the purpose of applying standard algorithms on graphs. <br>
The project originated as a project for the Algorithms course for the Master's degree in Stochastics and Data Science at the University of Turin.

# Notes

### PC requirements
- It has been tested on a pc with _Windows 11 (21H2)_;
- It requires a screen with resolution _1920x1080_.

### Software
The game runs on the venv khn_env_3.11 built on python 3.11.4 (with tkinter). <br>
After moving in the main folder of the game, the commands to create it are the following (on a cmd):
```
cd keep_heading_north
py -3.11 -m venv khn_env_3.11
.\khn_env_3.11\Scripts\activate
py -m pip install --upgrade pip
py -m pip install pywinauto
py -m pip install networkx
py -m pip install matplotlib
py -m pip install scipy
```

### Preliminaries
Create shortcut of the batch file which runs the game.
The batch is located in `keep_heading_north\code\run\run.bat`.
Open its properties:
- set the _Run_ option to _Maximized_;
- change icon with the one `keep_heading_north\code\source\images\khn.ico`.

# License

The content of this project itself is licensed under the [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/), and the underlying source code used to format and display that content is licensed under the [GNU General Public License v3.0](https://github.com/caporali/bsc_thesis/blob/main/LICENSE).