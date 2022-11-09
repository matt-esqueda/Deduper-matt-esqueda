#!/usr/bin/env python

import re
import argparse

def get_args():
    parser = argparse.ArgumentParser(description="Program for Velvet Assemblies")
    parser.add_argument('-f', help='file')
    parser.add_argument('-o', help='outfile')
    parser.add_argument('-u', help='umi')
    return parser.parse_args()

args = get_args()
f = args.f
o = args.o
u = args.u


# Dictionaries
read_cols = tuple()
read_set = set()
umi_set = set()
CIGAR_chars = ('S', 'M', 'D', 'N')
S_val, M_val, D_val, N_val = (0, 0, 0, 0)
header_line = 0
POS_adjusted = 0
duplicate_count = 0
umi_error = 0

with open(o, 'w') as out:

    # opens STL96 file and populates the UMI set with the list of acceptable UMIs
    with open(u, 'r') as u:
        for i, line in enumerate(u):
            line = line.strip('\n')
            umi_set.add(line)

        # opens the sam input file, and iterates through the lines of the file
        with open(f, 'r') as fh:
            for i, line in enumerate(fh):

                # this will write all of the header lines to the beginning of the output file and skip them when deduping
                if line[0] == '@':
                    header_line += 1
                    out.write(line)

                # extract the necessry columns for detecting duplicates
                else:
                    line_split = line.split('\t')
                    line_ID = line_split[0]
                    line_ID = line_ID.split(':')
                    umi, flag, chromosome, POS, CIGAR = line_ID[7], int(line_split[1]), (line_split[2]), int(line_split[3]), line_split[5]
                    read_cols = (umi, chromosome, POS_adjusted)
                    # print(read_cols)

                    # start by eliminating all UMIs that are not in the known UMI list (these are assumed to be errors)
                    if umi not in umi_set:
                        umi_error += 1
                        continue
                            
                    # FLAG
                    if ((flag & 16) == 16):
                        # strand = rev_comp
                        # print('rev_comp')
                        for char in CIGAR_chars:

                            if char not in CIGAR:
                                read_cols = (umi, chromosome, POS)
                            
                            elif char in CIGAR:
                            
                                # Look for S (at END) and adjust as necessary
                                if (char == "S") and ("S" == CIGAR[len(CIGAR) - 1]):
                                    S = re.findall(r'(\d+)S', CIGAR)
                                    S_val = int(S[len(S) - 1])

                                if char in CIGAR:
                                    M, D, N = re.findall(r'(\d+)M', CIGAR), re.findall(r'(\d+)D', CIGAR), re.findall(r'(\d+)N', CIGAR)
                                    # convert list of strings to list of integers
                                    M, D, N = list(map(int, M)), list(map(int, D)), list(map(int, N))
                                    # sum the values in the CIGAR string
                                    M_val, D_val, N_val = sum(M), sum(D), sum(N)
                                    # add the sums to POS to find adjusted POS
                                    POS_adjusted = POS + S_val + M_val + D_val + N_val
                                    read_cols = (umi, chromosome, POS_adjusted)
                                    # print(read_cols)

                        if read_cols not in read_set:
                            read_set.add(read_cols)
                            out.write(line)
                        elif read_cols in read_set:
                            duplicate_count += 1

                    else:
                        # print('forward')
                        # strand = forward
                        if "S" not in CIGAR:
                            read_cols = (umi, chromosome, POS)
                            # print(read_cols)
                        # Look for S (at BEGINNING) and adjust as necessary
                        elif "S" in CIGAR:
                            S = re.findall(r'(\d+)S', CIGAR)
                            if (len(S) == 2):
                                S_val = int(S[0])
                                POS_adjusted = POS + S_val
                            
                            elif (len(S) == 1) and ("S" != CIGAR[len(CIGAR) - 1]):
                                S_val = int(S[0])
                                POS_adjusted = POS + S_val
                                read_cols = (umi, chromosome, POS_adjusted)

                            # print(read_cols)

                        if read_cols not in read_set:
                            read_set.add(read_cols)
                            out.write(line)
                        elif read_cols in read_set:
                            duplicate_count += 1

                       
print(f'header lines: {header_line}')
print(f'umi error: {umi_error}')                                       
print(f'unique reads: {len(read_set)}')
print(f"duplicates: {duplicate_count}")
