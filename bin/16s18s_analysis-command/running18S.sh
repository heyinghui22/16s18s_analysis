#!/bin/bash

# Try to find the path to conda
echo "Checking conda path..."
CONDA_PATH=$(which conda)

if [ -z "$CONDA_PATH" ]; then
    echo "Conda not found. Please ensure it is installed and in your PATH."
    exit 1
fi

echo "Conda found at: $CONDA_PATH"

# Get the Conda directory by removing /bin/conda from the path
CONDA_DIR=$(dirname $(dirname "$CONDA_PATH"))  # Get the parent directory of the bin directory

# Initialize Conda using the correct path
if [ -f "$CONDA_DIR/etc/profile.d/conda.sh" ]; then
    source "$CONDA_DIR/etc/profile.d/conda.sh"
else
    echo "Conda initialization script not found!"
    exit 1
fi

# Activate the environment
conda activate M16_18seq-Extractor

# Run other commands after activating the environment
# For example:
# your_command_here

# Create log file
touch log

# Redirect standard output and standard error to files and screens
exec &> >(tee -a log) 1>&2 

echo "Please bring input files into a folder named 'illu', and enter the illu pathway"
echo "The file must be in .fastq format"
echo "Only one single-end sequencing sequence is needed"


# Receives the DATA_PATH argument passed by the main script
DATA_PATH="$1"
cd $DATA_PATH
for filename in "$DATA_PATH/illu/"*; do
  basename="${filename##*/}"
  name="${basename%.*}"
  echo "$name" >> list1
done

source activate M16_18seq-Extractor
mkdir seqkit
# Get the path
DATA_PATH="$1"
for i in `less $DATA_PATH/list1`; do
    seqkit fq2fa $DATA_PATH/illu/${i}.fastq -o $DATA_PATH/seqkit/${i}.fasta
done

mkdir rRNA_prediction
# Configure Python version 
conda deactivate
source activate M16_18seq-Extractor_p2.7

export PATH=./16s18s_analysis-scripts/rRNA_prediction/rRNA_hmm_fs_wst_v0:$PATH
DATA_PATH="$1"
./16s18s_analysis-scripts/rRNA_prediction/scripts/rRNA_hmm_run_wst_v0.pl $DATA_PATH/seqkit/ $DATA_PATH/rRNA_prediction

conda deactivate
# Extract 18S rRNA 
mkdir 18S
DATA_PATH="$1"
for i in $DATA_PATH/rRNA_prediction/*seq; do
    a=${i##*/}
    b=${a%%.*}
    perl ./16s18s_analysis-scripts/tiqu18s.pl $i $DATA_PATH/18S/$b.18s.fa
done

source activate M16_18seq-Extractor
DATA_PATH="$1"
for filename in "$DATA_PATH/18S"/*; do
  basename="${filename##*/}"
  name="${basename%.*}"
  echo "$name" >> list4
done

# Extract v9 area of 18S rRNA 
DATA_PATH="$1"
mkdir v9
for i in `less $DATA_PATH/list4`; do
    hmmsearch --cpu 4 --notextw --tblout $DATA_PATH/18S/${i}_V9.txt ./16s18s_analysis-scripts/rRNA_prediction/18s_v9/euk_v138_v9.hmm $DATA_PATH/18S/${i}.fa
    python ./16s18s_analysis-scripts/rRNA_prediction/scripts/fasta.hmmpick.large2.py $DATA_PATH/18S/${i}.fa $DATA_PATH/18S/${i}_V9.txt
done
mv $DATA_PATH/18S/*.hmmpick.fasta $DATA_PATH/v9

