# DSLRPlate-Solver

This is a sample tool for a quick astrometry solution of your dslr images (even RAW!), not sure what you were looking at? Find out here!

This is actually a PyPI astrometry (Astrometry.net) wrapper/tool to simply read raw DSLR photos and give them an astrometry solution.

## Installation
### Python & pip
Of course you need Python and pip to be installed
### Make a venv
this is common while using PyPI packages in a controlled environment, they will be available only locally 
``` bash
python -m venv venv
(linux/macos) source venv/bin/activate
(win) venv\Scripts\activate.bat
```
be sure to activate the virtual environment every time you use the script. Otherwise you can run the python executable directly inside the venv folder.
### Install the requirements
Install all the dependencies
``` bash
pip install -r requirements.txt
```

## Usage
The solver suppors a variety of RAW camera formats (it uses rawpy, built upon LibRaw, here the list of [supported cameras](https://www.libraw.org/supported-cameras))

I left one test image (taken by a Canon 600D) into `testfiles/sample.cr2` it refers to NGC 4406

### Input file path
the main argument must be of course the file path

### Solve methods
|Type|Arguments (w/ examples)|
|---|:---:|
|RA/DEC Hint |`-ra` 12h26m36s<br>`-dec` 12d48m53s|
|Target Hint|`-t` NGC4406<br>(Simbad lookup)|
|Blind| `-b`|

### Output Settings
|Arguments|Description|
|---|---|
|`-o`|Outputs a mono WCS solved fits (float32) <br> without argument it deafaults to the same path|
|`-orgb`|Outputs a non standard RGB WCS solved fits (to be used with `-o` argument)|
|`-g`|Works and outputs the G channel, better for photometry (to be used with `-o` argument)|


### Other arguments
|Argument|Description|
|----|---|
|`-r`|Changes the search radius (defaults to 2°)|
|`-j`|Outputs json data|
|`-h`|Shows help|

### Examples of usage with test data
```bash
python solve.py testfiles/sample.cr2 -t NGC4406 -o
```
Target hint, fits output in the same directory
```bash
python solve.py testfiles/sample.cr2 -ra 12h26m36s -dec 12d48m53s -o -g
```
Coords hint, fits output in the same directory, green channel
```bash
python solve.py testfiles/sample.cr2 -b -o -j
```
Blind solve, fits output in the same directory, json output
## Output
|Variable|Unit|
|--|-|
|`Center RA`|HMS|
|`Center DEC`|DMS|
|`Pixel Scale`|"/px|
## Work in progress
**Note:** This is a work in progress.<br>
I've noticed a minor issue with the coordinate reference system  during point cloud generation, which may cause slight inaccuracies when calculating the actual image center.
A fix is in progress.