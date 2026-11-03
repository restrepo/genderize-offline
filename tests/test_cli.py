import csv
import json

import pytest

from genderize_offline import __version__
from genderize_offline.cli import main


def test_version(capsys):
    with pytest.raises(SystemExit) as e:
        main(["--version"])
    assert e.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_name(capsys):
    assert main(["name", "Kelandre", "BB"]) == 0
    assert json.loads(capsys.readouterr().out) == {"name": "Kelandre", "gender": "male", "probability": 0.9, "count": 2}


def test_csv(tmp_path):
    src = tmp_path / "in.csv"
    src.write_text("name,country_id\nZorana,BB\nXyzzy,AA\n", encoding="utf-8")
    dst = tmp_path / "out.csv"
    assert main(["csv", str(src), str(dst)]) == 0
    with open(dst, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert [(r["gender"], r["probability"]) for r in rows] == [("female", "0.8"), ("unknown", "0.0")]


def test_build(tmp_path, capsys):
    from conftest import WGND

    src = tmp_path / "w.csv"
    src.write_text(WGND, encoding="utf-8")
    assert main(["build", str(src), str(tmp_path / "c.tsv.gz")]) == 0
    assert "sha256" in capsys.readouterr().err
