Ocean 506 project to download and analyze data from the Ocean Gene Atlas
Skills used.
    Shell scripting.
    argparse.
    subprocesses.
    local modules.
    matplotlib and cartopy for beautiful figures
    Github repository management.
===============================================================================
Access
clone using: git clone https://github.com/delasislas/TARAOcean.git

PREPARATION:
You will need to install cartopy for map plots
    Several ways to do this, most straightforward is run: conda install cartopy
    Note that this will install dependencies, some of which may need updating
You may need to update modules like pandas.
Ensure shared/OGArequest.sh is executable
    Navigate to the shared folder.
    Type chmod +x OGArequest.sh

TO USE:
Scripts should be run in the order
    1) collection.py
    2) dataManipulation.py
    3) abundance_plots.py

===============================================================================
*abundance_plots.py
Usage: python abundance_plots.py -f filename -r rank
Example: python abundance_plots.py -f dataProc -r Genus

filename: output picklefile from dataManipulation.py
    Default to datProc.p if excluded
rank: taxonomic rank from which to make plots
    Default to Superfamily if excluded

For any number of directories in TARAOcean_output, this script will generate a
sample map, a scatterplot of total abundance vs. environmental parameters, and
global abundance plots of each member of the rank of choice (both as a combined
plot and as individual plots)
===============================================================================
*collection.py
Usage: python collection.py -j jobname -f filename
Example: python collection.py -j test -f search.txt

filename refers to the list of sequences to search for.
filename can refered to with an absolute or relative path.

This file also creates the input and output directories for the project.
===============================================================================
*dataManipulation.py

Note: this is hardcoded for narG, we could later make this more robust.
Saves data to TARAOcean_output as dataProc.p and a zipfile with the raw data.
===============================================================================
*search.txt
Example format of sequences to search for.
NOTE: sequences need to be in FASTA format to be able to be run.
NOTE: include "END OF SEQUENCE" at the end of every sequence.
===============================================================================
*shared/directory.py
Module for directory management help.
===============================================================================
*shared/TARA.py
Module to call the Ocean Gene Atlas request.
===============================================================================
*shared/OGArequest.sh
Shell script to request data for each sequence asked for.
Sends request as a query to OGA.
Returns with the data from the server and stores in output as jobname_uniqueid.
Displays an error, that doesn't affect the outcome.
===============================================================================
