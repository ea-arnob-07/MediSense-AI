from pathlib import Path


STATIC_DIR = Path(__file__).resolve().parents[1] / "app" / "static"


def test_final_ui_contract():
    html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    javascript = (STATIC_DIR / "app.js").read_text(encoding="utf-8")

    assert 'id="downloadJson"' not in html
    assert "downloadJson" not in javascript
    assert 'class="active" type="button" data-view="compact"' in html

    for social_url in (
        "https://www.linkedin.com/in/estiuk-arafat-arnob-0350ba34a/",
        "https://github.com/ea-arnob-07/",
        "https://www.facebook.com/ea.arnob.07/",
    ):
        assert social_url in html

    assert '<span>Developed by</span><strong>Estiuk Arafat Arnob</strong>' in html
    assert "Designed &amp; Developed by <strong>Estiuk Arafat Arnob</strong>" in html
