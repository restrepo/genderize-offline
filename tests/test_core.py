import gzip

from genderize_offline import country_code, dictionary, genderize, guess, tokens


def test_build_is_reproducible(compact, tmp_path):
    src = tmp_path / "w.csv"
    from conftest import WGND

    src.write_text(WGND, encoding="utf-8")
    again = tmp_path / "again.tsv.gz"
    dictionary.build(src, again)
    assert dictionary.sha256(again) == dictionary.sha256(compact)


def test_compact_lines(compact):
    lines = gzip.decompress(compact.read_bytes()).decode().splitlines()
    assert lines == sorted(lines)
    assert "zorana\t0.9\t2\tAA:1,BB:0.8" in lines
    assert "miren\t1\t1\t" in lines  # accent-free alias


def test_country_first_then_average():
    assert guess("Zorana", "BB") == ("female", 0.8, 2)
    assert guess("Zorana", "CC") == ("female", 0.9, 2)
    assert guess("Zorana") == ("female", 0.9, 2)


def test_country_changes_gender():
    assert guess("Kelandre", "AA") == ("female", 0.6, 2)
    assert guess("Kelandre", "BB") == ("male", 0.9, 2)


def test_first_known_name_decides():
    assert guess("Q. Xyzzy Tomislavo Zorana", "AA") == ("male", 1.0, 1)


def test_unknown_and_unisex():
    assert guess("Xyzzy", "AA") == ("unknown", 0.0, 0)
    assert guess("", "AA") == ("unknown", 0.0, 0)
    assert guess("Ambo", "AA") == ("unknown", 0.0, 1)


def test_accents_both_ways():
    assert guess("Mirén")[0] == "female"
    assert guess("Miren")[0] == "female"


def test_tokens_and_country_code():
    assert tokens("Jean-Pierre A. B.") == ["jean", "pierre"]
    assert country_code("co") == "CO"
    assert country_code("Colombia") == "CO"
    assert country_code("Russian Federation") == "RU"
    assert country_code("Atlantis") == ""


def test_genderize_shape():
    assert genderize("Zorana", "BB") == {
        "count": 2,
        "name": "Zorana",
        "gender": "female",
        "probability": 0.8,
        "country_id": "BB",
    }
    assert genderize("Xyzzy")["gender"] is None
