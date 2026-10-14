"""Round 4 candidate contract regression; no publication or repository writes."""
from pathlib import Path
import re
from textwrap import dedent

import yaml


META = Path(__file__).resolve().parents[1]


def test_task_metadata_preserves_three_mode_string_contract():
    template = (META / "candidate/templates/skill-meta-x-ipe-task-based.md").read_text()
    match = re.search(r"    - name: process_preference.interaction_mode\n(.*?)(?=\n    - name:)", template, re.S)
    assert match is not None
    field = yaml.safe_load("name: interaction_mode\n" + dedent(match.group(1)))
    assert field["type"] == "string"
    assert field["default"] == "interact-with-human"
    for mode in ("interact-with-human", "dao-represent-human-to-interact",
                 "dao-represent-human-to-interact-for-questions-in-skill"):
        assert mode in field["description"]