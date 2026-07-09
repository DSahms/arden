"""PyInstaller runtime hook — set consumer edition on launch."""
import os

os.environ.setdefault("PERSONALOCK_EDITION", "consumer")
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
