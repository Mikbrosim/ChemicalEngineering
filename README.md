# Introduction
A collection of python scripts, for doing Chemical Engineering
## Material balances
Currently only supports **solving** and **drawing** *simple* material balances.
This will however likely change, as the course progresses.

Examples of a few material balances can be seen in [Examples](/examples). And an example of a drawing can be seen below

![drawing of example4.2-2](/examples/example4.2-2.png)

## Assistant for McCabe-Thiele Method
Currently the top of the python file most be modified as to contain the correct values
Afterwhich running the [script](/mccabe_thiele_method.py) results in a gui which helps with the calculation of destillation trays and R, given the relation between R_min and R alongside xD, zF, xB, q and an x-y diagram.
When the script is done, there should now be generated two files, one for the R_min drawing and one for the tray drawing. Along side this, it prints some relevant data for calculation of R_min, in the console.

Example of a tray drawing can be seen below

![drawing of trays](/examples/trays.png)

# Installation of everything
## Windows
1. Click [here](https://github.com/Mikbrosim/ChemicalEngineering/archive/refs/heads/main.zip) to download the lastest version as a zip file
2. Extract the zipfile into your chosen location
3. Execute the `install_for_windows.py`, which should install `graphviz` alongside `pydot`, `sympy`, `tkinter` and `pillow` if they are not installed already

## Linux
1. You'll figure it out! 😁

# Usage
## McCabe-Thiele Method
1. Take a screenshot of the x-y diagram and save it in the same folder as the script.
2. Modify the values at the top of the python file, `img_name`, `xD`, `zF`, `xB`, `q`, `R_relation`. The colors and sizes of the lines can also be adjusted as you wish.
3. Run the script.
4. Left-click on two diagonally opposing corners of the x-y diagram, a box should appear. If it aligns with the edges of the graph press enter, if not, right-click to try again.
5. Click the intersection of the x-y plot and the proposed q-line, a new line should appear. If it looks as expected press enter, if not, right-click to try again.
6. Click the intersection of the R_min-line and the q-line, such that the new line comes as close to the x-y plot as possible without hitting it. If it looks as expected press enter, if not, right-click to try again.
7. Click the intersection of the tray-line. Repeat until xB has been passed. At that point press enter. To go back a tray, right click

## Material balances
Coming ... sometime