# VASP HPC Computation

[English](#english) · [中文](#中文)

---

<a id="english"></a>

## English

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

### What it does

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

### Repository layout

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

### How to load this skill

- **TRADE / Claude skills (single `SKILL.md`)**: point the framework at this
  repo. `SKILL.md` is the entry instruction.
- **Codex / WorkBuddy plugin**: write a thin `plugin.json` that references
  `SKILL.md` as the entry instruction. No code changes are needed.
- **OpenCode / OpenClaw / custom agents**: paste the relevant sections of
  `SKILL.md` (Core principle, Routing logic, Async pattern, Safety rules) into
  the agent's system prompt and add `bin/` to `PATH`.
- **No-skill runtime**: just use `bin/` and `scripts/` directly from a shell.

### Configuration

Every connection parameter is env-overridable. `bin/hpc-common` sources
`~/.config/vasp-hpc-computation/env` automatically if it exists, so you can set
everything once. Copy `.env.example` there and fill in your values:

```bash
mkdir -p ~/.config/vasp-hpc-computation
cp .env.example ~/.config/vasp-hpc-computation/env
$EDITOR ~/.config/vasp-hpc-computation/env
```

#### Environment variables

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

#### SSH config

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

### Bundled commands

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

### Async-first workflow (critical)

VASP jobs run hours to days. Never wait for completion in-session.

1. **Submit phase** (current session): prepare inputs → upload → submit →
   record Job ID → return to the user immediately.
2. **Record**: `hpc-submit` appends a JSON row to `${HPC_JOB_LOG}` (Job ID,
   HPC dir, calc type, submit time, status).
3. **Tell the user**: "Job 1654321 submitted, ETA 8-12h. Next time just ask
   'Is Job 1654321 done?'"
4. **Check phase** (next session): `hpc-monitor` → if `COMPLETED`, parse
   results; if `RUNNING`, report progress.

See `SKILL.md` for the full routing logic, INCAR parameter principle,
monitoring & repair quick reference, and safety rules.

### Templates

`templates/INCAR.opt` and `templates/INCAR.neb` are **starting points only**.
For every new structure, search the literature / web for analogous systems and
compare candidate settings before committing. See the "INCAR parameter
principle" section in `SKILL.md`.

`templates/submit_opt.sh` and `templates/submit_neb.sh` are Slurm submit
scripts for a 24-core CPU node: `source /etc/profile.d/modules.sh`,
`module load ${VASP_MODULE}`, `cd $SLURM_SUBMIT_DIR`,
`mpirun -np $SLURM_NTASKS vasp_std`.

### Safety rules

- Never overwrite raw calculation outputs; write derived files under
  `analysis/` or `parsed/`.
- Never delete calculation directories automatically.
- Never change scientific settings (functional, dispersion, ENCUT, KPOINTS,
  force field, charges, NEB path) without explicitly reporting it.
- Default to `--dry-run` for resubmission; submit only when the user explicitly
  asks.
- Treat AI-generated scripts as drafts until tested on a small directory.

### License

MIT — see [LICENSE](LICENSE).

---

<a id="中文"></a>

## 中文

一个**框架无关、自包含的 skill**，将多孔材料的 RASPA / VASP / CI-NEB
理论计算任务转化为可审计、半自动化的工作流，运行在通过固定 SSH 中转访问的
HPC 集群上：

```text
macOS -> WSL 中转 -> HPC 登录节点
```

仓库根目录*即* skill 本身。任何能读取 Markdown 指令文件并调用 shell 脚本的
agent 框架都能加载它（TRADE / Claude skills、Codex / WorkBuddy、OpenCode、
OpenClaw、自定义 agent 等）。运行时不需要任何框架特定的清单文件。

所有连接参数均由环境变量驱动 —— 仓库内**不硬编码任何主机、用户名、端口或
密钥路径**。

### 功能

- 准备 VASP/RASPA 项目目录与模板。
- 通过 WSL 中转将本地计算目录上传至 HPC。
- 用 `hpc-submit` 提交 Slurm 作业并在本地记录作业 ID。
- 用 `hpc-monitor` 查询 `squeue` / `sacct` 状态。
- 用 `hpc-download` 下载已完成的输出目录。
- 用内置 Python 脚本解析 VASP / RASPA / NEB 输出。
- 强制执行**异步优先**的 VASP 工作流纪律：提交、记录、返回；稍后再解析。
- 通过 `SKILL.md` 中的路由逻辑将任务分派到匹配的 reference 与脚本。

### 仓库结构

```text
vasp-hpc-computation/
├── SKILL.md              # 入口指令（将你的 agent 框架指向这里）
├── README.md             # 本文件
├── LICENSE               # MIT
├── .env.example          # 环境配置模板
├── .gitignore
├── bin/                  # Shell 辅助命令（HPC 连接 / 提交 / 监控 / 传输）
│   ├── hpc-common        # 共享 env 与辅助函数，被每个命令 source
│   ├── hpc-connect
│   ├── hpc-submit
│   ├── hpc-monitor
│   ├── hpc-upload
│   └── hpc-download
├── scripts/              # Python 解析器与项目工具
├── templates/            # INCAR.opt、INCAR.neb、submit_opt.sh、submit_neb.sh
└── references/           # 路由逻辑分派到的深度 SOP
```

### 如何加载本 skill

- **TRADE / Claude skills（单一 `SKILL.md`）**：将框架指向本仓库，
  `SKILL.md` 即入口指令。
- **Codex / WorkBuddy 插件**：写一个薄薄的 `plugin.json`，引用 `SKILL.md`
  作为入口指令即可，无需改动代码。
- **OpenCode / OpenClaw / 自定义 agent**：将 `SKILL.md` 中的相关章节
  （核心原则、路由逻辑、异步模式、安全规则）粘贴进 agent 的 system prompt，
  并将 `bin/` 加入 `PATH`。
- **无 skill 运行时**：直接在 shell 中使用 `bin/` 与 `scripts/`。

### 配置

每个连接参数都可通过环境变量覆盖。`bin/hpc-common` 会在
`~/.config/vasp-hpc-computation/env` 存在时自动 source 它，因此只需配置
一次。将 `.env.example` 复制到该路径并填入你的值：

```bash
mkdir -p ~/.config/vasp-hpc-computation
cp .env.example ~/.config/vasp-hpc-computation/env
$EDITOR ~/.config/vasp-hpc-computation/env
```

#### 环境变量

| 变量 | 默认值 | 含义 |
|----------|---------|---------|
| `WSL_HOST` | `wsl-relay` | macOS `~/.ssh/config` 中通往 WSL 中转的 SSH 别名 |
| `HPC_HOST` | `hpc-login` | WSL `~/.ssh/config` 中通往 HPC 登录节点的 SSH 别名 |
| `HPC_USER` | *（必填，无默认值）* | HPC 用户名 |
| `HPC_DATA_ROOT` | `/home/${HPC_USER}/data` | HPC 数据根目录 |
| `HPC_JOB_LOG` | `$HOME/.local/share/vasp-hpc-computation/hpc-jobs.jsonl` | 本地作业日志路径 |
| `HPC_SUBMIT_SCRIPT` | `submit.sh` | 每个作业目录内的 Slurm 提交脚本文件名（实际项目常用 `submit.slurm`） |
| `VASP_MODULE` | `vasp/6.4.2_intel` | VASP 模块名（NEB 请用 VTST 构建） |
| `VASP_PARTITION` | `cpu`（在 `#SBATCH` 中） | Slurm 分区名 |

#### SSH 配置

辅助命令假定两个 SSH 别名。默认为 macOS 上的 `wsl-relay` 与 WSL 内的
`hpc-login`。以下为示例配置 —— 请将占位符替换为你的真实信息。

macOS `~/.ssh/config`：

```sshconfig
Host wsl-relay
    HostName <WSL_HOST_IP>
    User <WSL_USER>
    Port 22
    ServerAliveInterval 30
    ServerAliveCountMax 3
```

WSL `~/.ssh/config`：

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

> 若你的 SSH 别名不同，可在配置中重命名，或覆盖 `WSL_HOST` / `HPC_HOST`。

### 内置命令

```bash
bin/hpc-connect --check
bin/hpc-connect hostname
bin/hpc-monitor
bin/hpc-upload ./vasp_case /home/${HPC_USER}/data/vasp_case
bin/hpc-submit /home/${HPC_USER}/data/vasp_case
bin/hpc-download /home/${HPC_USER}/data/vasp_case/OUTCAR ./outputs/
```

单命令覆盖：

```bash
HPC_HOST=hpc-login HPC_USER=your_username hpc-connect --check
HPC_SUBMIT_SCRIPT=submit.slurm hpc-submit /home/your_username/data/vasp_project/host
```

### 异步优先工作流（关键）

VASP 作业运行数小时至数天。**绝不**在会话内等待完成。

1. **提交阶段**（当前会话）：准备输入 → 上传 → 提交 → 记录作业 ID →
   立即返回给用户。
2. **记录**：`hpc-submit` 向 `${HPC_JOB_LOG}` 追加一行 JSON（作业 ID、
   HPC 目录、计算类型、提交时间、状态）。
3. **告知用户**："Job 1654321 已提交，预计 8-12h。下次来问 'Job
   1654321 算完了吗' 即可。"
4. **查询阶段**（下次会话）：`hpc-monitor` → 若 `COMPLETED`，解析结果；
   若 `RUNNING`，汇报进度。

完整路由逻辑、INCAR 参数原则、监控与修复速查、安全规则见 `SKILL.md`。

### 模板

`templates/INCAR.opt` 与 `templates/INCAR.neb` **仅为起点**。
对于每个新结构，应先检索文献 / 网络上的同类体系，比较候选参数后再确定。
参见 `SKILL.md` 的"INCAR 参数原则"章节。

`templates/submit_opt.sh` 与 `templates/submit_neb.sh` 是面向 24 核 CPU 节点
的 Slurm 提交脚本：`source /etc/profile.d/modules.sh`、
`module load ${VASP_MODULE}`、`cd $SLURM_SUBMIT_DIR`、
`mpirun -np $SLURM_NTASKS vasp_std`。

### 安全规则

- 绝不覆盖原始计算输出；派生文件写入 `analysis/` 或 `parsed/`。
- 绝不自动删除计算目录。
- 绝不在未显式报告的情况下更改科学设置（泛函、色散校正、ENCUT、KPOINTS、
  力场、电荷、NEB 路径）。
- 重提交默认使用 `--dry-run`；仅当用户明确要求时才真正提交。
- 将 AI 生成的脚本视为草稿，先在小目录上测试再投入使用。

### 许可证

MIT —— 见 [LICENSE](LICENSE)。
