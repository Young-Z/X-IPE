"""Compatibility shim - redirects to x_ipe.app."""
from x_ipe.app import *

if __name__ == "__main__":
    from x_ipe.app import create_app, socketio
    app = create_app()
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)
