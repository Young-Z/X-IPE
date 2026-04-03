"""Tests for Task Board Page route — FEATURE-057-A.

Validates:
- GET /task-board returns 200 HTML
- Template extends base.html
- Required DOM elements present (stats, filters, table, pagination)
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


class TestTaskBoardPageRoute:
    """GET /task-board — page route tests."""

    def test_returns_200(self, client):
        resp = client.get("/task-board")
        assert resp.status_code == 200

    def test_returns_html_content_type(self, client):
        resp = client.get("/task-board")
        assert "text/html" in resp.content_type

    def test_contains_page_title(self, client):
        resp = client.get("/task-board")
        html = resp.data.decode()
        assert "Task Board" in html

    def test_contains_stat_cards_container(self, client):
        resp = client.get("/task-board")
        html = resp.data.decode()
        assert 'id="tb-stats"' in html

    def test_contains_table_element(self, client):
        resp = client.get("/task-board")
        html = resp.data.decode()
        assert 'id="tb-table"' in html

    def test_contains_table_headers(self, client):
        resp = client.get("/task-board")
        html = resp.data.decode()
        for col in ["Task ID", "Type", "Description", "Role", "Status", "Updated", "Output", "Next"]:
            assert col in html

    def test_contains_filter_bar(self, client):
        resp = client.get("/task-board")
        html = resp.data.decode()
        assert 'id="tb-search"' in html
        assert 'id="tb-status-filter"' in html

    def test_contains_range_toggles(self, client):
        resp = client.get("/task-board")
        html = resp.data.decode()
        assert 'data-range="1w"' in html
        assert 'data-range="1m"' in html
        assert 'data-range="all"' in html

    def test_contains_status_filter_options(self, client):
        resp = client.get("/task-board")
        html = resp.data.decode()
        for status in ["All Statuses", "In Progress", "Done", "Completed", "Pending", "Blocked", "Deferred"]:
            assert status in html

    def test_contains_pagination_container(self, client):
        resp = client.get("/task-board")
        html = resp.data.decode()
        assert 'id="tb-pagination"' in html

    def test_contains_error_banner(self, client):
        resp = client.get("/task-board")
        html = resp.data.decode()
        assert 'id="tb-error"' in html

    def test_contains_empty_state(self, client):
        resp = client.get("/task-board")
        html = resp.data.decode()
        assert 'id="tb-empty"' in html
        assert "No tasks found" in html

    def test_links_task_board_css(self, client):
        resp = client.get("/task-board")
        html = resp.data.decode()
        assert "task-board.css" in html

    def test_links_task_board_js(self, client):
        resp = client.get("/task-board")
        html = resp.data.decode()
        assert "task-board.js" in html

    def test_extends_base_template(self, client):
        """Verify the page includes base.html markers (Bootstrap, etc.)."""
        resp = client.get("/task-board")
        html = resp.data.decode()
        # base.html includes Bootstrap CSS
        assert "bootstrap" in html.lower()
