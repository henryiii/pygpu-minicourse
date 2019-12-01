#!/bin/bash
# GPU job

#SBATCH --job-name=cupy-job      # create a short name for your job
#SBATCH -o jupyterlab.out        # Name of stdout output file (%j expands to jobId)
#SBATCH --nodes=1                # node count
#SBATCH --ntasks=1               # total number of tasks across all nodes
#SBATCH --cpus-per-task=1        # cpu-cores per task (>1 if multi-threaded tasks)
#SBATCH --gres=gpu:tesla_v100:1  # number of gpus per node
#SBATCH --mem=1G                 # total memory (RAM) per node
#SBATCH --time=01:00:00          # total run time limit (HH:MM:SS)

module purge

echo "Job $SLURM_JOB_ID execution at: `date`"

NODE_HOSTNAME=`hostname -s`
LOCAL_PORT="8123"

eval "$(/opt/export/course/pygpu/miniconda/bin/conda shell.bash hook)"
conda activate gpu-minicourse

echo ""
echo "Your jupyter lab server is about to start!"
echo "To connect:"
echo "    ssh -J $USER@adroit $NODE_HOSTNAME -L $LOCAL_PORT:localhost:$LOCAL_PORT"
echo "The web address and token should be listed below."
echo "Manually cancel with:"
echo "    scancel $SLURM_JOB_ID"
echo ""

# Execution holds here until user clicks quit or time runs out

jupyter lab --no-browser --port=$LOCAL_PORT 

echo "job $SLURM_JOB_ID execution finished at: `date`"

