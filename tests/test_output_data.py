import json
from pathlib import Path

from src.schema import validate_digest


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"


def test_committed_digest_json_files_are_valid_and_conflict_free():
    failures: list[str] = []
    for path in OUTPUT_DIR.glob("*/digest.json"):
        raw = path.read_text(encoding="utf-8")
        if any(marker in raw for marker in ("<<<<<<<", "=======", ">>>>>>>")):
            failures.append(f"{path}: contains git conflict markers")
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            failures.append(f"{path}: invalid JSON: {exc}")
            continue
        ok, errors = validate_digest(data)
        if not ok:
            failures.append(f"{path}: {'; '.join(errors)}")

    assert failures == []
