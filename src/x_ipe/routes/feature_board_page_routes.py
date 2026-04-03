"""Feature Board Page Route — serves the Feature Board web page.

Blueprint: feature_board_page_bp
Endpoints:
  GET /feature-board — Feature Board HTML page

Location: src/x_ipe/routes/feature_board_page_routes.py
Feature: FEATURE-057-B
"""

from flask import Blueprint, render_template

from x_ipe.tracing import x_ipe_tracing

feature_board_page_bp = Blueprint("feature_board_page", __name__)


@feature_board_page_bp.route("/feature-board")
@x_ipe_tracing()
def feature_board():
    """Serve the Feature Board web page."""
    return render_template("feature-board.html")
