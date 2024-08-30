#!/bin/bash
#SBATCH --nodes=1  
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24    # There are 24 CPU cores on P100 Cedar GPU nodes
#SBATCH --mem=8gb               # Request the full memory of the node
#SBATCH --time=01:00:00 # 12h
#SBATCH --account=def-lutellie
#SBATCH --mail-user=diany_press@usp.br
#SBATCH --mail-type=ALL
hostname
module load python/3.9 gcc/9.3.0 arrow/11 cuda/11.4 rust/1.70.0 pandas/2.1.1 
virtualenv --no-download ~/tm_with_coherence
source ~/tm_with_coherence/bin/activate

cd ~/projects/def-lutellie/dianyusp/dataScienceBugs/notebooks/topic_modeling


pip install scikit-learn==1.2.2
pip install bertopic
pip install gensim