"""Arden Desktop GUI entry point — consumer chat window."""

import os
import typer

from modules.gui.chat_app import run_chat_app

app = typer.Typer()


@app.command()
def chat():
    """Open the Arden Desktop chat window (no terminal required)."""
    run_chat_app()


@app.command()
def smoke():
    """Headless consumer check (memory + optional Groq). For post-build verify."""
    from modules.consumer_smoke import run_consumer_smoke

    raise SystemExit(run_consumer_smoke())


if __name__ == "__main__":
    import sys

    # Double-click / Arden.exe — no subcommand required
    if len(sys.argv) == 1:
        run_chat_app()
    elif len(sys.argv) == 2 and sys.argv[1] in ("smoke", "smoke-test"):
        from modules.consumer_smoke import run_consumer_smoke

        code = run_consumer_smoke()
        if getattr(sys, "frozen", False):
            os._exit(code)
        raise SystemExit(code)
    elif len(sys.argv) == 2 and sys.argv[1] in ("acceptance", "acceptance-test"):
        from modules.arden_acceptance import run_acceptance

        code = run_acceptance()
        if getattr(sys, "frozen", False):
            os._exit(code)
        raise SystemExit(code)
    elif len(sys.argv) == 2 and sys.argv[1] in ("consigliere-test", "consigliere-acceptance"):
        from modules.consigliere_acceptance import run_consigliere_acceptance

        code = run_consigliere_acceptance()
        if getattr(sys, "frozen", False):
            os._exit(code)
        raise SystemExit(code)
    elif len(sys.argv) == 2 and sys.argv[1] in ("diagnose", "diagnose-test"):
        from modules.arden_diagnose import run_diagnose

        code = run_diagnose()
        if getattr(sys, "frozen", False):
            os._exit(code)
        raise SystemExit(code)
    else:
        app()
