"""
test_run.py — Headless test runner

Invokes the analysis pipeline directly (no Streamlit UI) using the two sample
datasets in sample_data/.  Prints the full report to stdout and writes it to
sample_data/test_report.md so it can be reviewed outside the terminal.

Usage:
    python test_run.py [--mode controlled|freerange] [--effort low|medium|high]
"""

import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))

from controllers.data_connector import DataConnector


def make_mock_file(path: Path):
    """
    Wraps a local file so DataConnector can call .read() and .seek() on it,
    matching the interface of a Streamlit UploadedFile.
    """
    class MockFile:
        def __init__(self, p: Path):
            self.name         = p.name
            self.originalname = p.name
            self._data        = p.read_bytes()
            self._pos         = 0

        def read(self):
            return self._data

        def seek(self, pos):
            self._pos = pos

    return MockFile(path)


def run(mode: str, effort: str):
    base = Path(__file__).parent / "sample_data"
    human_file = make_mock_file(base / "human_sessions.csv")
    agent_file  = make_mock_file(base / "agent_sessions.csv")

    connector = DataConnector()

    if mode == "controlled":
        result = connector.run_analysis(
            human_file   = human_file,
            agent_file   = agent_file,
            game_name    = "Project Nova (Sample)",
            test_date    = "2026-10-28",
            mode         = "controlled",
            effort_level = effort,
            goal_data    = {
                "target_problem":   (
                    "Does the agent exploit the wood sell/buy trading loop to accumulate "
                    "gold faster than the intended economy allows?"
                ),
                "success_criteria": (
                    "Agent logs show repeated sell_wood → buy_wood cycles in the same session "
                    "that result in net gold gain, and human logs show no equivalent pattern."
                ),
                "focus_areas": ["economy", "trading"],
                "context": (
                    "The trade system was added in the last patch. Wood sells for 25g and "
                    "costs 20g to buy back — a 5g net gain per cycle that may be unintended."
                ),
            },
            bounds_data = None,
        )
    else:
        result = connector.run_analysis(
            human_file   = human_file,
            agent_file   = agent_file,
            game_name    = "Project Nova (Sample)",
            test_date    = "2026-10-28",
            mode         = "freerange",
            effort_level = effort,
            goal_data    = None,
            bounds_data  = {
                "game_parameters": (
                    "Turn-based strategy game. Players start with 50g, 5 wood, 20 food. "
                    "Each turn they choose one action: gather resources, build structures "
                    "(farm, barracks), train soldiers, explore, trade, or attack. "
                    "Victory condition: destroy the enemy base. Soldiers cost 20g + 5 food. "
                    "Barracks cost 20g + 5 wood. Farms cost 20g + 5 wood and increase food cap. "
                    "Wood trades at 25g sell / 20g buy."
                ),
                "scope_limit":   "ignore food starvation edge cases",
                "max_findings":  8,
                "priority_hint": "economy exploits and win-rate differences",
            },
        )

    report   = result["report"]
    metadata = result["metadata"]

    print("\n" + "="*70)
    print(f"  ANALYSIS COMPLETE — {metadata['game_name']}")
    print(f"  Mode: {mode.upper()}  |  Effort: {effort.upper()}  |  Date: {metadata['test_date']}")
    print("="*70 + "\n")
    print(report)

    out_path = base / f"test_report_{mode}_{effort}.md"
    out_path.write_text(report)
    print(f"\n[Saved to {out_path}]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode",   choices=["controlled", "freerange"], default="freerange")
    parser.add_argument("--effort", choices=["low", "medium", "high"],   default="medium")
    args = parser.parse_args()
    run(args.mode, args.effort)
