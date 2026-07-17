# CI-NEB Diffusion-Barrier Workflow

## Purpose

Use CI-NEB when selectivity may be controlled by diffusion through a pore aperture, window, gate, channel bottleneck, or framework deformation.

## Workflow

1. Optimize the initial adsorption state (IS).
2. Optimize the final adsorption state (FS).
3. Ensure IS and FS have identical atom order, cell, and composition.
4. Generate 5-9 intermediate images using interpolation or IDPP.
5. Inspect all images for atomic overlap and discontinuous guest orientation.
6. Run NEB with climbing image.
7. Parse image energies and compute barrier:

```text
Ea = max(E_images) - E_initial
```

8. Inspect the highest-energy image and verify it corresponds to a physical diffusion bottleneck.
9. For rigorous work, frequency validation or additional TS refinement may be needed.

## Flexible-framework caution

For flexible PCP/MOF systems, the transition state is a coupled guest-framework state. It may include guest translation, guest rotation, ligand motion, pore-window expansion, and host-guest interaction loss. Do not freeze the entire framework unless the scientific goal is a rigid-framework approximation.

## Checks

- Are images continuous?
- Is the highest-energy image near the expected aperture/window?
- Does increasing image count change the barrier significantly?
- Is the barrier referenced to the correct initial state?
- Is the final state actually a local minimum?
