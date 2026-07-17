# RASPA Workflow Guide

## Role in the workflow

RASPA is used for low-cost adsorption-site search, MC/GCMC sampling, and generating initial host-guest configurations for higher-level VASP calculations.

## Standard RASPA adsorption-site search

1. Prepare framework CIF and verify cell parameters.
2. Choose framework LJ parameters, often UFF or a validated MOF force field.
3. Assign framework charges, often DDEC/REPEAT/DFT-derived charges when electrostatics matter.
4. Choose guest force field, such as TraPPE for common small gases and hydrocarbons when available.
5. Use Ewald summation for electrostatics in periodic systems.
6. Run equilibration cycles, then production cycles.
7. Extract representative adsorption configurations or probability density sites.
8. Convert selected configurations into VASP POSCARs.

## Template checklist

- ensemble: canonical MC, GCMC, or Widom insertion;
- temperature and pressure/loading;
- framework name and unit cell/supercell;
- molecule definition;
- force field files;
- charges;
- number of cycles;
- random seed if reproducibility is required;
- output frequency.

## Typical output to parse

- absolute adsorption loading;
- excess adsorption loading;
- average host-guest energy;
- block averages and uncertainties;
- final coordinates or movies when available.

## Caveats

RASPA force fields are normally used for sampling and trend exploration. Do not present force-field MC energies as final DFT binding energies unless the study is explicitly force-field-based.
