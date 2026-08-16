import json
from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def load_fixture(name: str):
    with open(FIXTURES_DIR / name) as fh:
        return json.load(fh)
