# tsukiyo

Tsukiyo is a program that displays and rotates various polytopes in 4D.

## Basics

### Requirements

- Python 3.5 with Tkinter

Probably works on earlier versions too. Definitely does not work on Python 2.

### Installation

    $ git clone https://github.com/eyqs/tsukiyo.git/
    $ cd tsukiyo/
    $ python tsukiyo.py

## Usage

Type in Schlafli or Wythoff symbols to generate a polytope, then rotate it
by pressing the big Rotate buttons or by using the left and right arrow keys.
Press the smaller buttons under Rotate to change the current rotation axis;
xw, yw, and zw are equivalent to rotating about the x-, y-, and z-axis in 3D.

Select the checkboxes to toggle various options, such as staying in 3D mode,
and slide the sliders to change various angles, for the camera and lighting.
Click the Colours menu to adjust various colours, such as for faces and menus.
Hold the distance and zoom buttons to change the camera's distance and zoom,
or use the up and down arrow keys to move closer or further from the polytope.

### Features

Supported Schlafli symbols:
- `{3}, {4}, {5}, ..., {10}` (triangle to decagon)
- `{5/2}, {5/3}, {7/2}, {7/3}, ..., {9/4}, {10/3}` (pentagram to decagram)
- `{3,3}, {3,4}, {3,5}, {4,3}, {5,3}` (Platonic solids)

Supported Wythoff symbols:
- `(2 2 2), (2 2 3), ..., (2 2 15)` (square to triacontagonal bipyramids)
- `(2 2 | 2), (2 2 | 3), ..., (2 2 | 10)` (square to decagon)
- `(3 2 | 2), ..., (6 2 | 2)` (triangular to hexagonal prisms)
- `(2 2 2 | ), (2 2 3 | )` (square and hexagonal prisms)
- `(3 3 2)` with all bar positions (tetrakis hexahedron symmetries)
- `(4 3 2)` with all bar positions (disdyakis dodecahedron symmetries)
- `(5 3 2)` with all bar positions (disdyakis triacontahedron symmetries)
- `(4 3/2 2), (4/3 3/2 2), (5 5/2 2), (5 5/3 2), (5/3 3 2), (5/3 3/2 3)`
with all bar positions, and probably many more. I have no idea what they are.

Unsupported, but coming soon:
- `{1}, {2}` (point, line)
- `{11}, {12}, ..., {n}` (all regular polygons)
- `{11/2}, {11/3}, {11/4}, ..., {n/d}` (all regular star polygons)
- `{5/2,5}, {5,5/2}, {5/2,3}, {3,5/2}` (Kepler-Poinsot polyhedra)
- `{3,3,3}, {4,3,3}, {3,3,4}, {3,4,3}, {5,3,3}, {3,3,5}` (regular 4-polytopes)
- `(2 2 16), (2 2 17), ..., (2 2 n)` (all bipyramids)
- `(2 2 4 |), (2 2 5 |), ..., (2 2 n |)` (all prisms)
- `(| 2 2 2), (| 2 2 3), ..., (| 2 2 n)` (all antiprisms)
- `(| 2 2 5/2), (| 2 2 7/2), ..., (| 2 2 n/d)` (all star antiprisms)

## History

I started this program in September 2014 as my Extended Essay in Mathematics
for the International Baccalaureate program. Later, I decided I could get away
with using it as my Internat Assessment in Mathematics for the blah blah too.
Afterwards, it sat in my projects folder being unfinished and annoying until
I decided to tidy it up and release it in February 2016. Here it is, Tsukiyo.

### Credits

Tsukiyo is created by Eugene Y. Q. Shen.

Thanks to my Extended Essay supervisor, Noriko Waight.

Moon logo based on <https://commons.wikimedia.org/wiki/File:FullMoon2010.jpg>

## License

Copyright &copy; 2014, 2015, 2016 Eugene Y. Q. Shen.

Tsukiyo is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version
3 of the License, or (at your option) any later version.

Tsukiyo is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License in [LICENSE.md][] for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

[license.md]:                ../master/LICENSE.md
                               "The GNU General Public License"
