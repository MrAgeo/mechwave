# README
[Spanish Version](README_es.md)

## Overview

**_Mechwave_** is an app that simulates the interaction of a mechanical wave with two or more mediums. Its purpose is to experiment with the characteristics of each simulated material.

## Video (Spanish)
The project's video and an introduction to the program itself can be found [here](https://www.youtube.com/watch?v=lg9X_b6Rx4o).

## Dependencies
**_MechWave_** depends on:
- `python3`
- `PyQt5`
- `matplotlib`
- `numpy`
- `meshio`

## How to run Mechwave
In order to run **_MechWave_**, you have to clone this repo and execute the main file (`base/mechwave_main.py`). Then, the main window will open.
Here you can import a mesh ('Archivo >  Importar malla'), edit the materials ('Opciones > Definir > Materiales'), assign the materials to the previously-defined element sections (e.g., through [gmsh](http://gmsh.info/#Download)), and observe the wave amplitude through the materials. 

_Note:_ Currently, **_Mechwave_** only supports gmsh's MSH files.
 
## License
**_MechWave_** is distributed under the [GPLv3](http://www.gnu.org/licenses/gpl-3.0.html) license.
