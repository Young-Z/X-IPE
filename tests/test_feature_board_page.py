"""Tests for Feature Board Page route — FEATURE-057-B.

Validates:
- GET /feature-board returns 200 HTML
- Template extends base.html
- Required DOM elements present (epics container, filters, error/empty states)
- CSS and JS assets linked
"""

import pytest

from x_ipe.app import create_app


@pytest.fixture()
def client(tmp_path):
    app = create_app()
    app.config["TESTING"] = True
    app.config["PROJECT_ROOT"] = str(tmp_path)
    with app.test_client() as c:
        yield c


class TestFeatureBoardPageRoute:
    """GET /feature-board — page route tests."""

    def test_returns_200(self, client):
        resp = client.get("/feature-board")
        assert resp.status_code == 200

    def test_returns_html_content_type(self, client):
        resp = client.get("/feature-board")
        assert "text/html" in resp.content_type

    def test_contains_page_title(self, client):
        resp = client.get("/feature-board")
        html = resp.data.decode()
        assert "Feature Board" in html

    def test_contains_epics_container(self, client):
        resp = client.get("/feature-board")
        html = resp.data.decode()
        assert 'id="fb-epics"' in html

    def test_contains_search_input(self, client):
        resp = client.get("/feature-board")
        html = resp.data.decode()
        assert 'id="fb-search"' in html

    def test_contains_status_filter(self, client):
        resp = client.get("/feature-board")
        html = resp.data.decode()
        assert 'id="fb-status-filter"' in html

    def test_contains_status_options(self, client):
        resp = client.get("/feature-board")
        html = resp.data.decode()
        for status in ["All Statuses", "Planned", "Refined", "Designed", "Implemented", "Tested", "Completed", "Retired"]:
            assert status in html

    def test_contains_error_banner(self, client):
        resp = client.get("/feature-board")
        html = resp.data.decode()
        assert 'id="fb-error"' in html

    def test_contains_empty_state(self, client):
        resp = client.get("/feature-board")
        html = resp.data.decode()
        assert 'id="fb-empty"' in html
        assert "No features found" in html

    def test_links_feature_board_css(self, client):
        resp = client.get("/feature-board")
        html = resp.data.decode()
        assert "feature-board.css" in html

    def test_links_feature_board_js(self, client):
        resp = client.get("/feature-board")
        html = resp.data.decode()
        assert "feature-board.js" in html

    def test_extends_base_template(self, client):
        resp = client.get("/feature-board")
        html = resp.data.decode()
        assert "bootstrap" in html.lower()
