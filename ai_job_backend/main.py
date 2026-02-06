"""
Entrypoint for the FastAPI application.

Delegates to api.main to keep the package layout tidy.
"""

import sys

from api.main import app

if __name__ == "__main__":
    import uvicorn

    # Disable reload on Windows to avoid PermissionError (WinError 5) from multiprocessing named pipes
    use_reload = sys.platform != "win32"
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=use_reload)
