# Literature Method Extraction

## Use case

Use when the user provides methods text, supplementary information, or a paper and wants an automated workflow reconstructed from it.

## Extraction schema

Return a table with these fields:

| Category | Extract |
|---|---|
| Scientific purpose | adsorption sites, binding energy, diffusion barrier, selectivity, correction |
| Adsorbates | molecule names, formulas, loading |
| Framework/material | name, phase, supercell, flexibility treatment |
| RASPA settings | ensemble, cycles, temperature, pressure, force fields, charges, Ewald, LJ cutoff if reported |
| VASP settings | version, functional, dispersion, PAW/POTCAR family, ENCUT, k-points, force convergence, ISIF if reported |
| NEB settings | initial/final sites, number of images if reported, force convergence, TS verification |
| Energy definitions | BE/Eads formula, sign convention, Ea formula |
| Corrections | MP2, MP2.5, BSSE, counterpoise, cluster model details |
| Missing information | any unreported but needed settings |
| Workflow logic | why this sequence was used |

## Output pattern

1. **Protocol table** with extracted values.
2. **Automation translation**: folder tree and scripts needed to reproduce the workflow.
3. **Assumptions and missing data**: identify unreported details that must not be invented.
4. **Course-report statement**: explain how AI extracts a reusable computational protocol from literature.

## Red flags

- Equations lost during PDF extraction.
- Molecule labels swapped or inconsistent.
- Force-field parameters not fully reported.
- DFT correction terms described but formula omitted.
- Energies reported in different units.
- Binding energy sign convention inconsistent across papers.
