"""Task Board Page Route — serves the Task Board web page.

Blueprint: task_board_page_bp
Endpoints:
  GET /task-board — Task Board HTML page

Location: src/x_ipe/routes/task_board_page_routes.py
Feature: FEATURE-057-A
"""

from flask import Blueprint, render_template

from x_ipe.tracing import x_ipe_tracing

task_board_page_bp = Blueprint("task_board_page", __name__)


@task_board_page_bp.route("/task-board")
@x_ipe_tracing()
def task_board():
    """Serve the Task Board web page."""
    return render_template("task-board.html")
