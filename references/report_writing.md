# Course Report Writing Guide

## Framing

For course reports, frame the skill as an AI application case in the user's own field:

**AI agents for automated theoretical-computation workflows**, especially RASPA/VASP adsorption and diffusion studies.

## Recommended report sections

1. Abstract
2. Keywords
3. Background: theory calculations are multi-step workflows, not one command.
4. Problem description: repetitive input generation, monitoring, parsing, repair, reproducibility.
5. Research progress: AiiDA, FireWorks, atomate, pymatgen, custodian, and current AI-agent skill frameworks for computational workflows.
6. Proposed method: a single self-contained skill that orchestrates literature extraction, RASPA, VASP, monitoring, repair, parsing, and reporting.
7. Experiment: use sample OUTCAR/RASPA outputs to demonstrate automatic parsing and adsorption-energy calculation.
8. Summary and outlook: AI assists workflow construction, not physical judgment.
9. References.

## Thesis statement

AI should not replace DFT, MC, NEB, or researcher judgment. Its value is converting fragile manual operations into auditable, reusable, semi-automated workflows.

## Suggested figures

- Main-agent/subagent architecture diagram.
- RASPA to VASP to NEB workflow diagram.
- Manual workflow vs AI-assisted workflow comparison table.
- Example parsed adsorption-energy table.
- Monitoring and repair state machine.
