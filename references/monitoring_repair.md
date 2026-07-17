# Monitoring, Repair, and Resubmission

## Status classes

Classify each job as:

- `not_started`: input files exist but no output.
- `running_or_incomplete`: output exists but no final convergence marker.
- `converged`: final energy and convergence marker found.
- `failed_known`: known error pattern found.
- `failed_unknown`: output exists but no recognized status.
- `needs_human_review`: scientific or structural anomaly.

## Common VASP technical issues

These are examples of technical repairs. Always report the proposed change.

| Symptom | Possible action |
|---|---|
| ionic relaxation hit NSW but forces decreasing | continue from CONTCAR with larger NSW |
| electronic convergence difficult | suggest safer ALGO, larger NELM, or smaller mixing after human approval |
| ZBRENT or line-search issues | suggest smaller POTIM or different IBRION after human approval |
| missing WAVECAR/CHGCAR for restart | restart from structure only |
| NEB image crashes due to bad geometry | inspect and regenerate images |

## Do not auto-repair

Do not automatically change:

- functional;
- dispersion correction;
- U values;
- spin state;
- charge state;
- supercell;
- k-point density;
- force-field parameters;
- adsorption site definition;
- NEB endpoints.

## Resubmission rule

Default to dry-run. Print the command that would be run. Submit only when the user explicitly requests actual submission.
