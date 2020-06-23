import os
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser("This script parses amber mdout files to extract the total energy. You can also use it to create plots.")
    parser.add_argument("path", help="The filepath to the file(s) to be analyzed. To analyze multiple files, you can use the `*` pattern.", type=str)
    parser.add_argument("--make_plots", help="Create a line plot of the values.", action='store_true')

    args = parser.parse_args()

    f = open(args.path)
    data = f.readlines()
    f.close()

    # Figure out the file name
    fname = os.path.basename(args.path).split('.')[0]

    etot = []
    # Loop through the lines
    for line in data:
        split_line = line.split()
        if 'Etot' in line:
            etot.append(float(split_line[2]))

    # Get rid of values we don't need.
    values = etot[:-2]
    # Open a file for writing
    outfile_location = F'{fname}_Etot.txt'
    outfile = open(outfile_location, 'w+')

    for value in values:
        outfile.write(f'{value}\n')

    outfile.close()