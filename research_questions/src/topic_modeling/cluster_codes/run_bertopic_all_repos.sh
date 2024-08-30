#!/bin/bash
#SBATCH --nodes=1 
#SBATCH --gpus-per-node=p100:1   
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1    # There are 24 CPU cores on P100 Cedar GPU nodes
#SBATCH --mem=16gb               # Request the full memory of the node
#SBATCH --time=12:00:00 
#SBATCH --account=def-lutellie
#SBATCH --mail-user=diany_press@usp.br
#SBATCH --mail-type=ALL

hostname
module load python/3.10 gcc/9.3.0 arrow/11 cuda/11.4 rust/1.70.0  
source ~/temp5/bin/activate
cd ~/projects/def-lutellie/dianyusp/dataScienceBugs/notebooks/topic_modeling

python bertopic_all_repos.py