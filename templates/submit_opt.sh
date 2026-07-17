#!/bin/bash
#SBATCH --job-name=vasp_opt
#SBATCH --partition=cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=24
#SBATCH --time=72:00:00
#SBATCH --output=vasp_%j.out
#SBATCH --error=vasp_%j.err
#
# Generic VASP geometry-optimization submit script.
# Before submitting, edit the #SBATCH lines above to match your cluster
# (partition name, ntasks-per-node, walltime). The VASP module can be
# overridden at submit time without editing this file:
#   export VASP_MODULE=vasp/vasp6.4.2_vtst_intel
# or pass sbatch options through hpc-submit:
#   hpc-submit <job-dir> --partition=intel --ntasks-per-node=24

# Make environment modules available (no-op on clusters that auto-load them).
source /etc/profile.d/modules.sh 2>/dev/null || true

# VASP module: override via the VASP_MODULE env var to fit your cluster.
module load "${VASP_MODULE:-vasp/6.4.2_intel}"

cd "$SLURM_SUBMIT_DIR"

# VASP optimization job. Use vasp_gam for gamma-only, vasp_ncl for SOC.
mpirun -np "$SLURM_NTASKS" vasp_std
