from __future__ import annotations

import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"


def run_step(script_name: str) -> None:
    result = subprocess.run([sys.executable, str(SRC_DIR / script_name)], cwd=BASE_DIR, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Step failed: {script_name}")


def main() -> None:
    run_step("generate_sample_data.py")
    run_step("build_analytics.py")
    print("Subscription analytics pipeline finished successfully.")


if __name__ == "__main__":
    main()
