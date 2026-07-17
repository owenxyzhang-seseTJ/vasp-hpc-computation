# VASP Adsorption-Energy Workflow

## Required calculations

For a single adsorbate:

1. host-only calculation;
2. isolated guest calculation in a large box;
3. host+guest calculation for each adsorption site.

Use the same exchange-correlation functional, dispersion correction, PAW/POTCAR family, ENCUT, and electronic convergence settings for comparable energies.

## Adsorption energy

Use:

```text
Eads = E(host+guest) - E(host) - E(guest)
```

For n guests:

```text
Eads_avg = [E(host+nG) - E(host) - n E(guest)] / n
```

Report the sign convention. Negative adsorption energy means exothermic/stabilizing adsorption under this convention.

## Recommended template fields

> These are starting points only. INCAR parameters must be decided **per structure**: search the literature/web for analogous systems (elements, open-shell vs closed-shell, metal vs insulator, transition metals, magnetism), compare candidate settings, and only then commit. Do not blindly copy a template.

- `ENCUT`: usually >= 500 eV or >= 1.3 * max ENMAX after convergence testing.
- `EDIFF`: 1e-5 or stricter.
- `EDIFFG`: -0.01 eV/A for optimized adsorption structures.
- `ISIF`: 2 for fixed-cell adsorption comparisons unless phase transition or equation of state is studied.
- `ISMEAR`: 0 with small SIGMA for molecular/insulating systems.
- `IVDW`: use a user-approved dispersion correction for physisorption.
- `LASPH`: recommended for accurate PAW gradient corrections, especially with metals.

## Folder pattern

```text
project/
  00_structures/
  01_raspa/
  02_vasp/
    host/
    guest/
    site_I/
    site_II/
  03_neb/
  analysis/
  logs/
```

## Validation

Before calculating adsorption energy:

- confirm all jobs converged;
- confirm final structures are physically reasonable;
- confirm the same POTCAR species order is used where appropriate;
- confirm all energies are final total energies, not intermediate ionic steps;
- confirm units.

## Result interpretation

Do not conclude selectivity solely from adsorption energy if the material is flexible or the separation is kinetic. Add deformation-energy analysis, diffusion barriers, or experimental comparison when needed.
