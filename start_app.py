import os, sys, time, subprocess, shutil
from pathlib import Path

# Cross-platform start script for backend Flask and frontend React dev servers

ROOT = Path(__file__).resolve().parent
backend_dir  = ROOT / "backend"
frontend_dir = ROOT / "frontend"
logs_dir = Path.home() / "app_logs"
logs_dir.mkdir(parents=True, exist_ok=True)

backend_log = open(logs_dir / "flask_backend.log", "a", buffering=1, encoding="utf-8")
frontend_log = open(logs_dir / "react_frontend.log", "a", buffering=1, encoding="utf-8")

IS_WINDOWS = os.name == "nt"

def pick_backend_python():
    """Return the Python executable from the backend venv, falling back to system python."""
    if IS_WINDOWS:
        venv_python = backend_dir / "venv" / "Scripts" / "python.exe"
        if venv_python.exists():
            return [str(venv_python)]
        # fallbacks if venv isn't found
        if shutil.which("py"):     return ["py", "-3"]
        if shutil.which("python"): return ["python"]
        return [sys.executable]
    else:
        for candidate in (backend_dir / "venv" / "bin" / "python3",
                          backend_dir / "venv" / "bin" / "python"):
            if candidate.exists():
                return [str(candidate)]
        # fallbacks
        if shutil.which("python3"): return ["python3"]
        if shutil.which("python"):  return ["python"]
        return [sys.executable]

def pick_backend_pip():
    """Return pip executable from the backend venv (or system pip as fallback)."""
    if IS_WINDOWS:
        for name in ("pip.exe", "pip3.exe"):
            p = backend_dir / "venv" / "Scripts" / name
            if p.exists():
                return str(p)
        return shutil.which("pip") or shutil.which("pip3") or "pip"
    else:
        for name in ("pip3", "pip"):
            p = backend_dir / "venv" / "bin" / name
            if p.exists():
                return str(p)
        return shutil.which("pip3") or shutil.which("pip") or "pip3"

def find_app_entry():
    for name in ("app.py", "main.py", "wsgi.py"):
        p = backend_dir / name
        if p.exists():
            return name
    print("[ERROR] Could not find app.py/main.py/wsgi.py in backend/", file=sys.stderr)
    sys.exit(1)

def pick_npm():
    return shutil.which("npm") or ("npm.cmd" if IS_WINDOWS else "npm")

def ensure_backend_dependencies():
    """Install backend requirements into venv if possible (best-effort)."""
    req = backend_dir / "requirements.txt"
    pip_cmd = pick_backend_pip()
    if req.exists() and pip_cmd:
        try:
            subprocess.run([pip_cmd, "install", "-r", str(req)], cwd=str(backend_dir), stdout=backend_log, stderr=backend_log, check=False)
        except Exception:
            pass

def ensure_frontend_dependencies(npm_cmd):
    """Run npm install if node_modules is missing (best-effort)."""
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        try:
            # Prefer ci if package-lock.json exists
            lock = frontend_dir / "package-lock.json"
            if lock.exists():
                subprocess.run([npm_cmd, "ci"], cwd=str(frontend_dir), stdout=frontend_log, stderr=frontend_log, check=False)
            else:
                subprocess.run([npm_cmd, "install"], cwd=str(frontend_dir), stdout=frontend_log, stderr=frontend_log, check=False)
        except Exception:
            pass

backend_py = pick_backend_python()
app_entry  = find_app_entry()
npm_cmd    = pick_npm()

# Ensure deps (non-blocking best-effort)
ensure_backend_dependencies()
ensure_frontend_dependencies(npm_cmd)

# Start Flask (from venv) and React
creationflags = 0  # set to subprocess.CREATE_NO_WINDOW for hidden windows

env_backend = os.environ.copy()

backend = subprocess.Popen(
    backend_py + [app_entry],
    cwd=str(backend_dir),
    stdout=backend_log, stderr=backend_log,
    creationflags=creationflags,
    env=env_backend
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
