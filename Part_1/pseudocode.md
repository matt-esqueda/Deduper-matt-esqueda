Problem:
PCR duplicates occur when there are mutiple sequencing reads from the same original genomic fragment. These duplicates are idenitied as sharing the same chromosome, position, strand, and UMI. Soft clipping and its effect of position also needs to be considered. They can introduce bias into the data so it is necessary for them to be identified and removed. The goal will be to create a removal tool that can take a properly sorted SAM file as input and remove all PCR duplicates, retaining only a single copy of each read in a properly formated output SAM file. 

Samtools sort will be used on the input SAM file to properly sort the file prior to performing duplicate removal

Test Files:
/home/mesqueda/bioinfo/Bi624/Deduper-matt-esqueda/unit_test_folder


Pseudocode

Use unix commands on the input sam file to remove all non-read lines and isolate the columns of interest. Can use a grep command to select and remove all lines beginning with "@". Cut the desired columns columns (1, 2, 3, 4, 6) and determine the best way to order the file (by chromosome or position?)


Search by chromosome for reads that have the same leftmost mapping position (POS). These will be the reads that need to be inspected for duplicates. Will need a way to look for reads that fit this criteria and also have identical UMI and strand. Also need a way to identify soft clipping which may change the POS. 

For this problem, we are using known UMIs. The provided UMIs file can be loaded into a list to be used to filter the reads. If a read contains a UMI not in the list, it can be assumed as an error and removed from the file.

Create and empty dictionary to hold {chromosome number / POS : UMI / Strand} 

- Open the output sam file which will be written to.
    - Open the input file to read from 
        -Iterate through the file by line
            -The first column will contain the UMI, discard the read if the UMI is not in the known list. 
            -Go chromosome by chromosome and look for reads that have the same POS (possible to reset dict for each chromosome??)
                * Will need a way to identify soft clipping, probably a function to recognize and adjust the POS accordingly?
                
                -Add that POS to the dictionary, along with the UMI and strand (+ or -) as tuple value 
                    * Will probably need a funtion(s) to return this information from the line directly
                -If that entry already exist in the dictionary, continue (don't add to dictionary)
                -Should result in a dictionary containing all of the unique reads for the SAM file 
                (I think this will work, might have to adjust the data structure)

- use the dictionary keys and values to write out the appropriate information to a properly formated output sam file


Functions

def UMI(line: str) -> str:
    ''' Takes the line from the file as an argument and returns the associated UMI in the first column '''
    return UMI
    Ex: NS500451:154:HWKTMBGXX:1:11101:24260:1121:AGGTTGCT	16	2	100	36	10M     Returns: AGGTTGCT

def strand(line: str) -> str:
    ''' Takes the line form the file as an argument and uses bit flag 16 to determine whether the string is + or - '''
    return strand_value (+ or -)
    Ex: NS500451:154:HWKTMBGXX:1:11101:24260:1121:AGGTTGCT	16	2	100	36	10M     Returns: -

def POS(line: str) -> int:
    ''' Takes the line from the file as an argument and returns the POS from the fourth column '''
    return POS
    Ex: NS500451:154:HWKTMBGXX:1:11101:24260:1121:AGGTTGCT	16	2	100	36	10M     Returns: 100

def soft_clip(line: str) -> int:
    ''' Takes the line from the file as an arguement and uses the CIGAR string to determine if soft clipping is present at the left most position. Returns the corrected POS value if so... still haven't figured this out (maybe need two functions?)
    return POS
    Ex: IDK