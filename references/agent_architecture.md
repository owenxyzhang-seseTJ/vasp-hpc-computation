# Agent Architecture for RASPA/VASP Workflows

## Purpose

Use this reference when designing a course-report workflow, a group computational protocol, or a multi-agent automation plan.

## Main agent

The main workflow agent owns the plan and audit trail. It should:

1. restate the scientific goal;
2. classify the task as adsorption-site search, DFT adsorption energy, diffusion barrier, output parsing, or monitoring;
3. assign subagents;
4. require human approval for scientific settings;
5. write a run log.

## Subagents

### Literature-method agent

Input: paper/SI text, PDF-extracted methods, or user notes.
Output: a structured protocol containing software, model size, force field, charge model, MC settings, DFT settings, formulas, correction methods, and open questions.

### RASPA agent

Input: framework CIF, guest molecule, force field choice, charge model, ensemble, temperature/pressure/loading.
Output: RASPA folder tree, simulation.input draft, force-field checklist, and parsing commands.

### VASP input agent

Input: POSCAR/CIF/XYZ, calculation type, approved template.
Output: VASP folders, INCAR/KPOINTS checklist, submit script draft, and metadata.yaml.

### Monitor agent

Input: calculation root directory.
Output: status table with converged, unconverged, failed, running, and missing-output jobs.

### Repair agent

Input: error classification.
Output: a repair plan. It may propose copying CONTCAR to POSCAR, increasing NSW for unfinished ionic relaxation, or switching to a safer electronic minimization setting. It must ask before changing scientific parameters.

### Parser agent

Input: RASPA output, VASP OUTCAR/OSZICAR, NEB image directories.
Output: CSV/JSON summaries, adsorption energies, diffusion barriers, and warnings.

### Report agent

Input: workflow log, parsed tables, user’s course-report outline.
Output: methods paragraphs, workflow diagrams, result summaries, and limitations.

## Audit metadata

Each workflow root should include:

```yaml
project: project_name
created_by: ai-assisted workflow
human_owner: name_or_group
software:
  raspa: unknown
  vasp: unknown
approved_parameters:
  functional: PBE
  dispersion: D3BJ
  encut: 500
  kpoints: user_approved
status: draft
notes: []
```

## Required human approvals

Require explicit human approval before:

- changing functional, dispersion correction, pseudopotential family, U value, spin state, charge, supercell, or k-point density;
- resubmitting large batches;
- deleting or overwriting raw output;
- accepting a NEB barrier as physically meaningful;
- writing final mechanistic conclusions.
