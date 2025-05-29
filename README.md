# DSLRPlate-Solver

This is a sample tool for a quick astrometry solution of your dslr images (even RAW!), not sure what you were looking at? Find out here!

This is actually a PyPI astrometry (Astrometry.net) wrapper/tool to simply read raw DSLR photos and give them an astrometry solution.

## Installation
### Python & pip
Of course you need Python and pip to be installed
``` bash
pip install git+https://github.com/astrophil583/DSLRPlate-Solver
```

## Usage
> **_NOTE:_**  The code will download the catalog files into the `astrometry_cache` folder if not found. (Approx 300Mb) 

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
dslrplatesolver testfiles/sample.cr2 -t NGC4406 -o
```
Target hint, fits output in the same directory
```bash
dslrplatesolver testfiles/sample.cr2 -ra 12h26m36s -dec 12d48m53s -o -g
```
Coords hint, fits output in the same directory, green channel
```bash
dslrplatesolver testfiles/sample.cr2 -b -o -j
```
Blind solve, fits output in the same directory, json output
## Output
|Variable|Unit|
|--|-|
|`Center RA`|HMS|
|`Center DEC`|DMS|
|`Pixel Scale`|"/px|

# Library use
To use this package inside a python script, after installing it you can just 
```python
from dslrplatesolver import solve
#solve(
#     input: Any,
#     ra: Any,
#     dec: Any,
#     target: Any,
#     r: Any,
#     blind: bool = False
# ) -> list
```
## Work in progress
**Note:** This is a work in progress.<br>
This library is optimized to work with pixel scales around 1 "/pixel. It should be enough for most of the amateur astronomy photos taken with dsrl. Let me know through Issues if you need an extension of the pxscale range.