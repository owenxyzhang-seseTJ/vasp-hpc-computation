---
name: vasp-hpc-computation
description: Framework-agnostic skill that turns porous-material RASPA / VASP / CI-NEB theoretical-computation tasks into auditable, semi-automated workflows on an HPC cluster accessed through a macOS → WSL → HPC SSH relay. Covers adsorption energies, diffusion barriers, async job submission and tracking, monitoring, repair, and output parsing.
framework_agnostic: true
---

# VASP HPC Computation

A self-contained, vendor-neutral skill: the repository root *is* the skill.
Any agent framework that can read a Markdown instruction file plus call shell
scripts can load it (Claude/TRADE skills, Codex/WorkBuddy, OpenCode, OpenClaw,
custom agents, etc.). There are no framework-specific manifests required at
runtime — only the `bin/` helpers and the `scripts/`, `templates/`, `references/`
directories that ship alongside this file.

## How to load this skill

- If your framework reads a single `SKILL.md` (TRADE, Claude skills, etc.), point
  it at this file. The repository path is the skill root.
- If your framework uses a plugin manifest, write a thin wrapper that simply
  references `SKILL.md` as the entry instruction. No code changes are needed.
- If your framework has no skill concept, paste the relevant sections below
  (Core principle, Routing logic, Async pattern, Safety rules) into the agent's
  system prompt and add `bin/` to `PATH`.

Required user-side configuration (env vars or `~/.config/vasp-hpc-computation/env`):
`WSL_HOST`, `HPC_HOST`, `HPC_USER`. See `.env.example` and the README.

## Core principle

Turn porous-material theoretical-computation tasks into auditable,
semi-automated workflows on an HPC cluster. Separate **scientific decisions**
from **automation actions**:

- Human decides: model, physical question, functional/force field, convergence
  criteria, adsorption sites, diffusion path, final mechanism.
- Agent automates: directory structure, templates, scripts, checks, parsing,
  status summaries, restart suggestions, plots, report drafts.

Default scope: RASPA for MC/GCMC adsorption configuration search and VASP for
periodic DFT geometry optimization, adsorption energies, and CI-NEB diffusion
barriers.

## SSH connection to the HPC

Connection chain: **macOS → WSL relay → HPC login node**

All SSH/rsync/scp commands originate from macOS, relay through a WSL host to the
HPC. **Never SSH directly from macOS to the HPC.**

> All connection parameters (host aliases, usernames, ports, key paths) are
> env-overridable and **not hardcoded** anywhere in this skill. Defaults assume
> SSH aliases `wsl-relay` (on macOS) and `hpc-login` (inside WSL). `HPC_USER`
> is **required**. See `.env.example` and the repository README.

### Command template

```bash
# Remote command execution
ssh ${WSL_HOST} "ssh ${HPC_HOST} '<command>'"

# Upload: macOS → WSL → HPC
scp local_file ${WSL_HOST}:/tmp/
ssh ${WSL_HOST} "scp /tmp/local_file ${HPC_HOST}:<remote_path>/"

# Download: HPC → WSL → macOS
ssh ${WSL_HOST} "scp ${HPC_HOST}:<remote_path>/OUTCAR /tmp/"
scp ${WSL_HOST}:/tmp/OUTCAR ./
```

### Bundled HPC tools (`bin/`)

- `hpc-connect [command]`: open an interactive shell or run a command on the HPC.
- `hpc-submit <job-dir> [sbatch-opts]`: submit a Slurm job via `sbatch`. Honors
  `HPC_SUBMIT_SCRIPT` (default `submit.sh`; override when your project uses
  `submit.slurm`, `submit_core.sh`, etc.).
- `hpc-monitor [job-pattern]`: query `squeue`/`sacct` for job status.
- `hpc-upload <local> <remote>`: upload files to the HPC via `scp`.
- `hpc-download <remote> <local>`: download files from the HPC via `scp`.

All helpers source `bin/hpc-common`, which reads the env vars above and the
config file at `${CONFIG_FILE:-$HOME/.config/vasp-hpc-computation/env}`.

### HPC directory conventions

- User home: typically `/home/${HPC_USER}/` (override via `HPC_DATA_ROOT`).
- Data root: `${HPC_DATA_ROOT}` (default `/home/${HPC_USER}/data/`).
- VASP executable: check with `which vasp_std` or `module avail vasp`.
- Slurm scheduler: `sbatch <HPC_SUBMIT_SCRIPT>`, `squeue -u ${HPC_USER}`.

## Routing logic (single-agent direct dispatch)

When the skill is loaded by a single agent, route the task to the matching
reference + script. A multi-agent runtime may instead spawn one sub-agent per
route; both modes are valid.

1. User provides a paper / SI / methods paragraph → extract a computational
   protocol first. Use `references/literature_extraction.md` and
   `scripts/extract_methods_from_text.py`.
2. User wants a new project workflow → build a folder plan using
   `references/agent_architecture.md` and `scripts/generate_project_skeleton.py`.
3. Task involves RASPA input/output → use `references/raspa_workflow.md` and
   `scripts/parse_raspa_output.py`.
4. Task involves VASP adsorption energies → use `references/vasp_workflow.md`
   and `scripts/parse_vasp_energy.py`, `scripts/calc_adsorption_energy.py`,
   `scripts/check_vasp_convergence.py`.
5. Task involves diffusion barriers → use `references/neb_workflow.md` and
   `scripts/parse_neb_barrier.py`.
6. Task involves job monitoring, repair, or resubmission → use
   `references/monitoring_repair.md` and `scripts/monitor_and_resubmit.py`.
7. Task is a course report or group documentation → use
   `references/report_writing.md`.

## Standard RASPA → VASP → NEB workflow

For porous-material adsorption and diffusion studies:

1. **Literature extraction**: force field, charge model, MC cycles, supercell,
   DFT functional, cutoff, k-points, energy definitions.
2. **RASPA search**: canonical MC or GCMC to locate plausible adsorption sites.
3. **Structure transfer**: convert selected RASPA configurations into
   VASP-ready structures.
4. **VASP optimization**: optimize host, guest, and host+guest with consistent
   settings.
5. **Adsorption energy**: `Eads = E(host+guest) − E(host) − E(guest)`.
6. **Diffusion barrier**: if separation is kinetic, generate a CI-NEB path and
   compute `Ea = E_TS − E_IS`.
7. **Monitoring and repair**: classify errors; apply only reversible technical
   repairs automatically.
8. **Reporting**: methods, tables, mechanism-oriented interpretation.

## INCAR parameter principle (critical)

`templates/INCAR.opt` and `templates/INCAR.neb` are **starting points only**.
For every new structure:

1. Identify the chemistry (open-shell vs closed-shell, metal vs insulator,
   transition metals, magnetism, soft modes).
2. **Search the literature / web for analogous systems** and compare candidate
   settings (functional, ENCUT, ISMEAR/SIGMA, IVDW, ISPIN/MAGMOM, KPOINTS).
3. Only then commit to an INCAR. **Never blindly copy a template.**
4. Record the reasoning in `metadata.yaml` or `workflow_log.md` so the choice
   is auditable.

The templates already leave `ISPIN`, `MAGMOM`, `LREAL` etc. commented where a
per-system decision is required.

## Async job pattern (critical)

VASP calculations take hours to days. **Never wait for a job to finish
in-session.** Follow this pattern:

1. **Submit phase (current session)**: prepare inputs → upload → submit →
   record Job ID → return to user immediately.
2. **Record**: `hpc-submit` appends a JSON object to `${HPC_JOB_LOG}` (default
   `$HOME/.local/share/vasp-hpc-computation/hpc-jobs.jsonl`): Job ID, HPC
   directory, calculation type, submit time, status.
3. **Tell the user**: "Job `<id>` 已提交，预计 X h。下次来问 'Job `<id>`
   算完了吗' 即可。"
4. **Check phase (next session)**: user returns → read the job log → query
   `squeue`/`sacct` → if `COMPLETED`, proceed to result parsing; if `RUNNING`,
   report progress; if `FAILED`, route to monitoring/repair.

Job record shape (one JSON object per line):

```json
{"job_id":"1654321","hpc_dir":"/home/${HPC_USER}/data/vasp_project/host","calc_type":"geometry_optimization","submit_time":"2026-06-15T19:30:00+08:00","status":"submitted","notes":"host optimization for adsorption energy"}
```

## Monitoring & repair quick reference

Status classes: `not_started`, `running_or_incomplete`, `converged`,
`failed_known`, `failed_unknown`, `needs_human_review`.

Common technical repairs (always **report** the proposed change):

| Symptom | Possible action |
|---|---|
| Ionic relaxation hit NSW but forces still decreasing | continue from `CONTCAR` with larger `NSW` |
| Electronic convergence difficult | safer `ALGO`, larger `NELM`, smaller mixing (after approval) |
| `ZBRENT` / line-search issues | smaller `POTIM` or different `IBRION` (after approval) |
| Missing `WAVECAR`/`CHGCAR` for restart | restart from structure only |
| NEB image crashes on bad geometry | inspect and regenerate images |

**Do not auto-repair** scientific parameters: functional, dispersion, U values,
spin/charge state, supercell, k-point density, force-field parameters,
adsorption-site definition, NEB endpoints.

Resubmission rule: default to `--dry-run`. Submit only when the user explicitly
asks.

## Safety and audit rules

- Never overwrite raw calculation outputs. Derived files go under `analysis/`,
  `parsed/`, or timestamped directories.
- Never delete calculation directories automatically.
- Never change scientific settings (functional, IVDW, ENCUT, KPOINTS, force
  field, charges, NEB path) without explicitly reporting the change.
- For HPC resubmission, produce the command or use `--dry-run` by default
  unless the user explicitly asks to submit.
- Treat AI-generated scripts as drafts until tested on a small directory.
- Record every generated workflow in `workflow_log.md` or `metadata.yaml`.
- Verify SSH connectivity before any HPC operation.
- Check available modules and queue status before submitting.
- Log all HPC operations with timestamps.

## Output patterns

When the user asks for a workflow, provide: (1) folder tree, (2) step-by-step
workflow, (3) scripts to run, (4) parameter checklist, (5) validation
checklist, (6) expected outputs.

When the user asks for a script, provide executable code plus usage examples.

## Bundled scripts (`scripts/`)

- `generate_project_skeleton.py` — create a RASPA/VASP workflow folder skeleton.
- `parse_vasp_energy.py` — extract final TOTEN and convergence hints from
  OUTCAR/OSZICAR.
- `calc_adsorption_energy.py` — compute adsorption energies from host, guest,
  and host_guest energies.
- `check_vasp_convergence.py` — batch-check VASP job status.
- `parse_neb_barrier.py` — parse NEB image energies and compute the barrier.
- `parse_raspa_output.py` — extract common RASPA loading/energy values.
- `extract_methods_from_text.py` — heuristic extractor for computational-method
  paragraphs.
- `monitor_and_resubmit.py` — monitor VASP folders and prepare dry-run
  resubmission commands.

Always inspect script help with `python <script> --help` before using on user
data.

## Templates (`templates/`)

- `INCAR.opt`, `INCAR.neb` — starting-point INCAR files. See the INCAR
  parameter principle above; do not use verbatim.
- `submit_opt.sh`, `submit_neb.sh` — Slurm submit scripts (24 cores per node,
  `module load` via `/etc/profile.d/modules.sh`, `cd $SLURM_SUBMIT_DIR`,
  `mpirun -np $SLURM_NTASKS vasp_std`). Override the module name with
  `VASP_MODULE` (e.g. `vasp/vasp6.4.2_intel` or `vasp/vasp6.4.2_vtst_intel`
  for NEB).

## References (`references/`)

Deeper SOPs that the routing logic dispatches to:

- `agent_architecture.md` — folder plan, audit metadata, human-approval gates.
- `literature_extraction.md` — protocol extraction from papers/SI.
- `raspa_workflow.md` — RASPA MC/GCMC input and output.
- `vasp_workflow.md` — adsorption-energy calculations, validation, interpretation.
- `neb_workflow.md` — CI-NEB path setup and barrier parsing.
- `monitoring_repair.md` — status classification, technical-repair table,
  resubmission rule.
- `report_writing.md` — course-report / group-document structure.
