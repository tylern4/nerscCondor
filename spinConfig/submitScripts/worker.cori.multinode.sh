#!/bin/bash -l
#SBATCH -N 2
#SBATCH -q debug
#SBATCH -C haswell
#SBATCH -A nstaff
#SBATCH -t 00:05:00
#SBATCH --job-name=condor_worker
#SBATCH --exclusive

#SBATCH -e /global/homes/t/tylern/spin_condor/outputs/multinode_%j.err
#SBATCH -o /global/homes/t/tylern/spin_condor/outputs/multinode_%j.out

# Move to the correct folder
cd /global/homes/t/tylern/spin_condor

# For each node start a worker
echo $(date)": Starting Nodes "
for node in $(scontrol show hostnames ${SLURM_NODELIST}); do
    echo $node
    srun -N 1 -n 1 -c 1 --gres=craynetwork:1 --overlap start_worker.sh &
    sleep 2;
done;

# Sleep for a little less than the time limit
sleep 200

# For each node end a 
echo $(date)": Stopping Nodes "
for node in $(scontrol show hostnames ${SLURM_NODELIST}); do
    echo $node
    srun -N 1 -n 1 -c 1 --gres=craynetwork:1 --overlap stop_worker.sh &
    sleep 2;
done;
exit
