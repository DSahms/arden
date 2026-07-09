# -*- coding: utf-8 -*-
import sys
import subprocess
import time
import requests
import os
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_DIR = Path(__file__).resolve().parent


def print_status(msg):
    print(f"  {msg}")


def wait_for_service(name, url, timeout=60):
    print_status(f"Waiting for {name}...")
    for _ in range(timeout):
        try:
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
                print_status(f"{name} ready.")
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def start_docker_and_neo4j():
    print_status("Starting Docker Desktop...")
    docker_path = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if os.path.exists(docker_path):
        subprocess.Popen([docker_path])
        print_status("Waiting for Docker to initialize (30s)...")
        time.sleep(30)
    else:
        print_status("Docker Desktop not found at default path - please start manually.")
        input("Press Enter when Docker Desktop is running...")

    print_status("Starting Neo4j via docker compose...")
    subprocess.run(
        ["docker", "compose", "up", "-d"],
        cwd=PROJECT_DIR,
        capture_output=True,
    )


def ensure_ollama():
    try:
        r = requests.get("http://localhost:11434", timeout=2)
        if r.status_code == 200:
            print_status("Ollama already running.")
            return True
    except Exception:
        pass
    print_status("Starting Ollama...")
    subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NO_WINDOW)
    return wait_for_service("Ollama", "http://localhost:11434")


def check_docker_running():
    result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
    return result.returncode == 0


def ensure_kobold():
    try:
        r = requests.get("http://127.0.0.1:5001/v1/models", timeout=3)
        if r.status_code == 200:
            print_status("KoboldCpp ready on port 5001.")
            return True
    except Exception:
        pass
    print_status("KoboldCpp not detected on :5001 — start it before chatting.")
    return False


print()
print("=" * 50)
print("  SAM LAUNCHER")
print("=" * 50)

if not check_docker_running():
    start_docker_and_neo4j()
else:
    print_status("Docker is running.")
    print_status("Ensuring Neo4j container...")
    subprocess.run(
        ["docker", "compose", "up", "-d"],
        cwd=PROJECT_DIR,
        capture_output=True,
    )

if not ensure_ollama():
    print_status("ERROR: Ollama failed to start. Check installation.")
    input("Press Enter to exit.")
    sys.exit(1)

if not wait_for_service("Neo4j", "http://localhost:7474"):
    print_status("ERROR: Neo4j failed to respond. Check: docker compose logs neo4j")
    input("Press Enter to exit.")
    sys.exit(1)

ensure_kobold()

print()
os.chdir(PROJECT_DIR)
exec(open("daily_briefing.py", encoding='utf-8').read())

print()
print_status("Starting Sam...")
print()
os.execv(sys.executable, [sys.executable, "main_base_assistant.py"])
