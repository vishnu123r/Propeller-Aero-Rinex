# Project Title
This code extracts the rinex files for a given period and base from the FTP server at  ftp://www.ngs.noaa.gov/cors/rinex and merges into a single .obs file. 
This should be able to dowload files for any base between any period. 

## Getting Started

### Prerequisites

Python 3.6 should be installed in the computer. The installation file could be downloaded [here.](https://www.python.org/downloads/)

### Installing

Download the repo files to a "folder" of choice. MAKE SURE ALL FILES ARE IN THE SAME FOLDER.

## Deployment

* Open command line interface and set the "folder" as your working directory
* Three arguments will passed be need to be passed: 
    base - The base station ID 
    period1 - Collect data from this time
    period2 - to this time
* Periods must be in the following format: %Y-%m-%dT%H:%M:%SZ. Look at the example below for clarity.
* The python file need to be called in the command line with the  three arguments
```
python mergeRinex.py nybp 2017-10-06T22:11:22Z 2017-10-07T01:33:44Z

```
* Command line should start running the script as you hit enter. 

* If everything goes well script should merge the requested file and save it in the current directory under the name - <base>.obs
* A folder named 'zip_downloads' is created to save all the downloaded zip files from the server.
* Unzipped files are saved in the working directory and deleted once the merging is over. 

## Built With

* [Python](https://www.python.org/)

## Library attributions
* ftplib
* datetime
* string
* gzip
* os
* argparse
* fnmatch
* subprocess

* [TEQC toolkit](https://www.unavco.org/software/data-processing/teqc/teqc.html) - Used for merging RINEX files

## Acknowledgments

This wouldn't have been possible without you. - Stackoverflow

