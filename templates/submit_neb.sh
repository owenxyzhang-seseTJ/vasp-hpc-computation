#!/bin/bash
#SBATCH --job-name=vasp_neb
#SBATCH --partition=cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=24
#SBATCH --time=120:00:00
#SBATCH --output=neb_%j.out
#SBATCH --error=neb_%j.err
#
# Generic VASP CI-NEB submit script.
# Before submitting, edit the #SBATCH lines above to match your cluster
# (partition name, ntasks-per-node, walltime). NEB needs a VTST-enabled
# VASP build, so set VASP_MODULE accordingly, e.g.:
#   export VASP_MODULE=vasp/vasp6.4.2_vtst_intel

# Make environment modules available (no-op on clusters that auto-load them).
source /etc/profile.d/modules.sh 2>/dev/null || true

# VASP module: use a VTST-enabled build for NEB. Override via VASP_MODULE.
module load "${VASP_MODULE:-vasp/6.4.2_intel}"

cd "$SLURM_SUBMIT_DIR"

# CI-NEB diffusion-barrier calculation.
mpirun -np "$SLURM_NTASKS" vasp_neb
