# LÉEME

## Descripción
**_MechWave_** es una aplicación que simula por medio de elementos finitos la interacción de una onda con dos o más medios, permitiendo experimentar un poco con las propiedades de cada material a simular.

## Video
El video de explicación del proyecto, y una pequeña introducción al programa se puede encontrar en [este link](https://www.youtube.com/watch?v=lg9X_b6Rx4o).

## Dependencias
**_MechWave_** necesita para su ejecución:
- `python3`
- `PyQt5`
- `matplotlib`
- `numpy`
- `meshio`

## Ejecución
Sólo clona el repositorio y ejecuta el archivo `base/mechwave_main.py`.  Allí aparecerá una ventana donde se puede importar la malla, editar los materiales a simular, asignarlos a las selecciones de elementos previamente hechas (por ejemplo con [gmsh](http://gmsh.info/#Download)), y ver las amplitudes de las ondas a través del material. De momento sólo permite importar los tipos de archivos .MSH de gmsh. Sin embargo, en un futuro pondremos más.
 
## Licencia
**_MechWave_** se distribuye bajo la licencia [GPLv3](http://www.gnu.org/licenses/gpl-3.0.html).
