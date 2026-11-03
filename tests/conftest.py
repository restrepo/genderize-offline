import pytest

from genderize_offline import core, dictionary

# A synthetic WGND extract: made-up spellings and shares, not real data.
WGND = """name,code,gender,wgt
zorana,AA,F,1
zorana,BB,F,.8
zorana,BB,M,.2
tomislavo,AA,M,1
kelandre,AA,F,.6
kelandre,AA,M,.4
kelandre,BB,M,.9
kelandre,BB,F,.1
mirén,AA,F,1
ambo,AA,F,.5
ambo,AA,M,.5
"""


@pytest.fixture(scope="session")
def compact(tmp_path_factory):
    d = tmp_path_factory.mktemp("wgnd")
    src = d / "wgnd.csv"
    src.write_text(WGND, encoding="utf-8")
    dst = d / "compact.tsv.gz"
    dictionary.build(src, dst)
    return dst


@pytest.fixture(autouse=True)
def table(compact):
    core.use_table(dictionary.load(compact))
    yield
    core.use_table(None)
