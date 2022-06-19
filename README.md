# pgn_gif
## About The Project
Convert a PGN file, Lichess game URLs or Lichess Game IDs to .gif
Displays move, clock and evaluation.

![](https://github.com/DavidMcNamara/pgn_gif/blob/main/Example_game.gif)

### Built With
+ https://www.python.org/downloads/
+ https://python-chess.readthedocs.io/en/latest/core.html
+ https://pillow.readthedocs.io/en/stable/
+ https://requests.readthedocs.io/en/latest/
+ https://cairosvg.org/documentation/

### Prerequisites

A version of python compatible with ``requirements.txt``
````txt
CairoSVG==2.5.2
chess==1.6.1
Pillow==9.1.1
requests==2.26.0
````

### Installation
   ```bash
   git clone https://github.com/DavidMcNamara/pgn_gif.git
   pip install -r requirements.txt
   ```

<!-- USAGE EXAMPLES -->
## Usage
Used the help command for info on the available parameters
```bash
py pgn_gif.py --help
```
```txt
usage: PGN to GIF [-h] [-f FILENAME] [-w WEBSITE] [-i ID] [-c CLOCKS] [-e EVALS] [-l LITERATE] [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -f FILENAME, --file FILENAME
                        Add file path to a PGN file
  -w WEBSITE, --web WEBSITE
                        Add URL path to PGN
  -i ID, --id ID        Add Lichess Game ID
  -c CLOCKS, --clocks CLOCKS
                        Include clock comments in the PGN moves, when available
  -e EVALS, --evals EVALS
                        Include analysis evaluation comments in the PGN, when available
  -l LITERATE, --literate LITERATE
                        Insert textual annotations in the PGN about the opening, analysis variations, mistakes, and game termination
  -o OUTPUT, --output OUTPUT
                        Specify the output filename.
```
Example usage using a lichess game ID, including clock and evaluation information:
```bash
py pgn_gif.py -i xpruxY3x -e true -c true -o Example_game 
```