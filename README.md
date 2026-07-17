# VASP HPC Computation

A **framework-agnostic, self-contained skill** that turns porous-material
RASPA / VASP / CI-NEB theoretical-computation tasks into auditable,
semi-automated workflows on an HPC cluster accessed through a fixed SSH relay:

```text
macOS -> WSL relay -> HPC login node
```

The repository root *is* the skill. Any agent framework that can read a
Markdown instruction file and call shell scripts can load it (TRADE / Claude
skills, Codex / WorkBuddy, OpenCode, OpenClaw, custom agents, …). No
framework-specific manifests are required at runtime.

All connection parameters are environment-driven — **no host, username, port,
or key path is hardcoded** anywhere in this repo.

## What it does

- Prepare VASP/RASPA project folders and templates.
- Upload local calculation folders to the HPC through the WSL relay.
- Submit Slurm jobs with `hpc-submit` and record job IDs locally.
- Monitor `squeue` / `sacct` status with `hpc-monitor`.
- Download completed output folders with `hpc-download`.
- Parse VASP / RASPA / NEB outputs with bundled Python scripts.
- Enforce an **async-first** VASP workflow discipline: submit, record, return;
  parse later.
- Route tasks to the matching reference + script via the routing logic in
  `SKILL.md`.

## Repository layout

```text
vasp-hpc-computation/
├── SKILL.md              # Entry instruction (point your agent framework here)
├── README.md             # This file
├── LICENSE               # MIT
├── .env.example          # Template for the env config
├── .gitignore
├── bin/                  # Shell helpers (HPC connectivity / submit / monitor / transfer)
│   ├── hpc-common        # Shared env + helpers, sourced by every command
│   ├── hpc-connect
│   ├── hpc-submit
│   ├── hpc-monitor
│   ├── hpc-upload
│   └── hpc-download
├── scripts/              # Python parsers and project tooling
├── templates/            # INCAR.opt, INCAR.neb, submit_opt.sh, submit_neb.sh
└── references/           # Deep SOPs dispatched to by the routing logic
```

## How to load this skill

- **TRADE / Claude skills (single `SKILL.md`)**: point the framework at this
  repo. `SKILL.md` is the entry instruction.
- **Codex / WorkBuddy plugin**: write a thin `plugin.json` that references
  `SKILL.md` as the entry instruction. No code changes are needed.
- **OpenCode / OpenClaw / custom agents**: paste the relevant sections of
  `SKILL.md` (Core principle, Routing logic, Async pattern, Safety rules) into
  the agent's system prompt and add `bin/` to `PATH`.
- **No-skill runtime**: just use `bin/` and `scripts/` directly from a shell.

## Configuration

Every connection parameter is env-overridable. `bin/hpc-common` sources
`~/.config/vasp-hpc-computation/env` automatically if it exists, so you can set
everything once. Copy `.env.example` there and fill in your values:

```bash
mkdir -p ~/.config/vasp-hpc-computation
cp .env.example ~/.config/vasp-hpc-computation/env
$EDITOR ~/.config/vasp-hpc-computation/env
```

### Environment variables

| Variable | Default | Meaning |
|----------|---------|---------|
| `WSL_HOST` | `wsl-relay` | SSH alias (in macOS `~/.ssh/config`) reaching the WSL relay |
| `HPC_HOST` | `hpc-login` | SSH alias (in WSL `~/.ssh/config`) reaching the HPC login node |
| `HPC_USER` | *(required, no default)* | HPC username |
| `HPC_DATA_ROOT` | `/home/${HPC_USER}/data` | HPC data root directory |
| `HPC_JOB_LOG` | `$HOME/.local/share/vasp-hpc-computation/hpc-jobs.jsonl` | Local job log path |
| `HPC_SUBMIT_SCRIPT` | `submit.sh` | Slurm submit script filename inside each job dir (real projects often use `submit.slurm`) |
| `VASP_MODULE` | `vasp/6.4.2_intel` | VASP module name (use a VTST build for NEB) |
| `VASP_PARTITION` | `cpu` (in `#SBATCH`) | Slurm partition name |

### SSH config

The helpers assume two SSH aliases. The defaults are `wsl-relay` (on macOS) and
`hpc-login` (inside WSL). Example configs — replace the placeholders with your
real details.

macOS `~/.ssh/config`:

```sshconfig
Host wsl-relay
    HostName <WSL_HOST_IP>
    User <WSL_USER>
    Port 22
    ServerAliveInterval 30
    ServerAliveCountMax 3
```

WSL `~/.ssh/config`:

```sshconfig
Host hpc-login
    HostName <HPC_LOGIN_HOST>
    Port <HPC_PORT>
    User <HPC_USER>
    IdentityFile ~/.ssh/hpc_ed25519
    IdentitiesOnly yes
    BatchMode yes
    PreferredAuthentications publickey
    ServerAliveInterval 60
    ServerAliveCountMax 2
```

> If your SSH aliases differ, either rename them in your config or override
> `WSL_HOST` / `HPC_HOST`.

## Bundled commands

```bash
bin/hpc-connect --check
bin/hpc-connect hostname
bin/hpc-monitor
bin/hpc-upload ./vasp_case /home/${HPC_USER}/data/vasp_case
bin/hpc-submit /home/${HPC_USER}/data/vasp_case
bin/hpc-download /home/${HPC_USER}/data/vasp_case/OUTCAR ./outputs/
```

Per-command overrides:

```bash
HPC_HOST=hpc-login HPC_USER=your_username hpc-connect --check
HPC_SUBMIT_SCRIPT=submit.slurm hpc-submit /home/your_username/data/vasp_project/host
```

## Async-first workflow (critical)

VASP jobs run hours to days. Never wait for completion in-session.

1. **Submit phase** (current session): prepare inputs → upload → submit →
   record Job ID → return to the user immediately.
2. **Record**: `hpc-submit` appends a JSON row to `${HPC_JOB_LOG}` (Job ID,
   HPC dir, calc type, submit time, status).
3. **Tell the user**: "Job 1654321 已提交，预计 8-12h。下次来问 'Job
   1654321 算完了吗' 即可".
4. **Check phase** (next session): `hpc-monitor` → if `COMPLETED`, parse
   results; if `RUNNING`, report progress.

See `SKILL.md` for the full routing logic, INCAR parameter principle,
monitoring & repair quick reference, and safety rules.

## Templates

`templates/INCAR.opt` and `templates/INCAR.neb` are **starting points only**.
For every new structure, search the literature / web for analogous systems and
compare candidate settings before committing. See the "INCAR parameter
principle" section in `SKILL.md`.

`templates/submit_opt.sh` and `templates/submit_neb.sh` are Slurm submit
scripts for a 24-core CPU node: `source /etc/profile.d/modules.sh`,
`module load ${VASP_MODULE}`, `cd $SLURM_SUBMIT_DIR`,
`mpirun -np $SLURM_NTASKS vasp_std`.

## Safety rules

- Never overwrite raw calculation outputs; write derived files under
  `analysis/` or `parsed/`.
- Never delete calculation directories automatically.
- Never change scientific settings (functional, dispersion, ENCUT, KPOINTS,
  force field, charges, NEB path) without explicitly reporting it.
- Default to `--dry-run` for resubmission; submit only when the user explicitly
  asks.
- Treat AI-generated scripts as drafts until tested on a small directory.

## License

MIT — see [LICENSE](LICENSE).
