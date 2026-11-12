
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

SCRIPTS = [
    "src/analysis/sentiment.py",
    "src/integrations/upload_instagram_comments_to_daily.py"
]


def run_pipeline():

    print("\n================================")
    print("INSTAGRAM SENTIMENT TRACKER")
    print("Starting daily pipeline...")
    print("================================")

    for script in SCRIPTS:

        script_path = ROOT / script

        if not script_path.exists():
            print(f"\nERROR: Script not found: {script}")
            return

        print(f"\nRunning: {script}")

        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=ROOT
        )

        if result.returncode != 0:
            print(f"\nPipeline stopped. Error in: {script}")
            return

    print("\n================================")
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("================================")


if __name__ == "__main__":
    run_pipeline()
