# start_app.py (Windows)
import os, sys, time, subprocess, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
backend_dir  = ROOT / "backend"
frontend_dir = ROOT / "frontend"
logs_dir = Path.home() / "app_logs"
logs_dir.mkdir(parents=True, exist_ok=True)

backend_log = open(logs_dir / "flask_backend.log", "a", buffering=1, encoding="utf-8")
frontend_log = open(logs_dir / "react_frontend.log", "a", buffering=1, encoding="utf-8")

def pick_backend_python():
    # your venv is here:
    venv_python = backend_dir / "venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        return [str(venv_python)]
    # fallbacks if venv isn't found:
    if shutil.which("py"):      return ["py", "-3"]
    if shutil.which("python"):  return ["python"]
    return [sys.executable]

def find_app_entry():
    for name in ("app.py", "main.py", "wsgi.py"):
        p = backend_dir / name
        if p.exists():
            return name
    print("[ERROR] Could not find app.py/main.py/wsgi.py in backend/", file=sys.stderr)
    sys.exit(1)

def pick_npm():
    return shutil.which("npm") or "npm.cmd"

backend_py = pick_backend_python()
app_entry  = find_app_entry()
npm_cmd    = pick_npm()

# Start Flask (from venv) and React
creationflags = 0  # set to subprocess.CREATE_NO_WINDOW for hidden windows
backend = subprocess.Popen(
    backend_py + [app_entry],
    cwd=str(backend_dir),
    stdout=backend_log, stderr=backend_log,
    creationflags=creationflags
)

frontend = subprocess.Popen(
    [npm_cmd, "start"],
    cwd=str(frontend_dir),
    stdout=frontend_log, stderr=frontend_log,
    creationflags=creationflags
)

try:
    while True:
        if backend.poll() is not None or frontend.poll() is not None:
            break
        time.sleep(2)
finally:
    for p in (backend, frontend):
        try:
            if p and p.poll() is None:
                p.terminate()
        except Exception:
            pass
    backend_log.close()
    frontend_log.close()
