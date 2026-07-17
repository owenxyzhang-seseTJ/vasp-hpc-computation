#!/usr/bin/env python3
"""Generate an auditable RASPA/VASP workflow folder skeleton."""
from __future__ import annotations

import argparse
from pathlib import Path
from datetime import datetime

INCAR_OPT = """SYSTEM = adsorption_opt
ENCUT = 500
PREC = Accurate
EDIFF = 1E-5
EDIFFG = -0.01
IBRION = 2
NSW = 300
ISIF = 2
ISMEAR = 0
SIGMA = 0.05
GGA = PE
IVDW = 12
LASPH = .TRUE.
ADDGRID = .TRUE.
"""

KPOINTS_GAMMA = """Gamma
0
Gamma
1 1 1
0 0 0
"""

RASPA_TEMPLATE = """SimulationType                MonteCarlo
NumberOfCycles                300000
NumberOfInitializationCycles  100000
PrintEvery                    1000
Forcefield                    Local
UseChargesFromCIFFile         yes
Framework 0
FrameworkName                 FRAMEWORK_NAME
UnitCells                     1 1 1
ExternalTemperature           298.0
Movies                        yes
WriteMoviesEvery              1000
Component 0 MoleculeName      GUEST_NAME
            MoleculeDefinition Local
            TranslationProbability 1.0
            CreateNumberOfMolecules 1
"""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(text)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create RASPA/VASP workflow skeleton.")
    parser.add_argument("project")
    args = parser.parse_args()
    root = Path(args.project)
    dirs = [
        "00_literature",
        "01_structures/raw",
        "01_structures/processed",
        "02_raspa/site_search",
        "03_vasp/host",
        "03_vasp/guest",
        "03_vasp/host_guest/site_I",
        "03_vasp/host_guest/site_II",
        "04_neb/path_I_to_II",
        "analysis/tables",
        "analysis/figures",
        "logs",
        "templates/vasp",
        "templates/raspa",
    ]
    for d in dirs:
        (root / d).mkdir(parents=True, exist_ok=True)
    write(root / "templates/vasp/INCAR.opt", INCAR_OPT)
    write(root / "templates/vasp/KPOINTS.gamma", KPOINTS_GAMMA)
    write(root / "templates/raspa/simulation.input", RASPA_TEMPLATE)
    metadata = f"""project: {root.name}
created: {datetime.now().isoformat(timespec='seconds')}
status: draft
human_approval_required:
  - functional
  - dispersion
  - force_field
  - charges
  - kpoints
  - neb_path
notes: []
"""
    write(root / "metadata.yaml", metadata)
    write(root / "workflow_log.md", f"# Workflow log\n\nCreated {datetime.now().isoformat(timespec='seconds')}\n")
    print(f"created workflow skeleton at {root}")


if __name__ == "__main__":
    main()
