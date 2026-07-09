"""PyInstaller runtime hook — set Arden Desktop consumer edition on launch."""
import os
import sys

_bundle = getattr(sys, "_MEIPASS", "")
if _bundle and _bundle not in sys.path:
    sys.path.insert(0, _bundle)

try:
    from modules.arden_env import setdefault as arden_setdefault

    arden_setdefault("EDITION", "consumer")
    arden_setdefault("CONFIG", "assistant_config.consumer.yml")
except ImportError:
    os.environ.setdefault("ARDEN_EDITION", "consumer")
    os.environ.setdefault("ARDEN_CONFIG", "assistant_config.consumer.yml")

os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
