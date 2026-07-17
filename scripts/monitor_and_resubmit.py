#!/usr/bin/env python3
"""Monitor VASP folders and prepare dry-run resubmission commands."""
from __future__ import annotations

import argparse
import csv
import subprocess
from pathlib import Path


def classify(folder: Path) -> tuple[str, str]:
    outcar = folder / "OUTCAR"
    contcar = folder / "CONTCAR"
    submit = folder / "submit.sh"
    if not outcar.exists():
        return "not_started", "no OUTCAR"
    text = outcar.read_text(errors="ignore")
    if "reached required accuracy" in text:
        return "converged", "accuracy marker found"
    if "ZBRENT" in text:
        return "failed_known", "ZBRENT line search issue"
    if "BRMIX" in text:
        return "failed_known", "charge mixing issue"
    if contcar.exists() and contcar.stat().st_size > 0 and submit.exists():
        return "restart_candidate", "CONTCAR and submit.sh exist"
    return "needs_review", "no convergence marker"


def main() -> None:
    parser = argparse.ArgumentParser(description="Monitor VASP jobs and optionally resubmit restart candidates.")
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--submit-cmd", default="sbatch submit.sh", help="Command to run inside job folder")
    parser.add_argument("--execute", action="store_true", help="Actually submit restart candidates. Default is dry run.")
    parser.add_argument("-o", "--output", default="monitor_status.csv")
    args = parser.parse_args()

    root = Path(args.root)
    folders = sorted({p.parent for p in root.rglob("OUTCAR")})
    rows = []
    for folder in folders:
        status, reason = classify(folder)
        command = args.submit_cmd if status == "restart_candidate" else ""
        rows.append({"folder": str(folder), "status": status, "reason": reason, "command": command})
        if args.execute and command:
            print(f"submitting in {folder}: {command}")
            subprocess.run(command, cwd=folder, shell=True, check=False)
        elif command:
            print(f"dry-run: cd {folder} && {command}")

    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["folder", "status", "reason", "command"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {args.output} with {len(rows)} rows")


if __name__ == "__main__":
    main()
