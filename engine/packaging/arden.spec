# PyInstaller spec — Arden Desktop consumer edition
# Build: pyinstaller packaging/arden.spec
# Output: dist/Arden/Arden.exe

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules

root = Path(SPECPATH).parent

_chroma_datas, _chroma_binaries, _chroma_hidden = collect_all('chromadb')
_rust_datas, _rust_binaries, _rust_hidden = collect_all('chromadb_rust_bindings')
_wry_datas, _wry_binaries, _wry_hidden = [], [], []

a = Analysis(
    [str(root / 'main_gui_assistant.py')],
    pathex=[str(root)],
    binaries=_chroma_binaries + _rust_binaries + _wry_binaries,
    datas=[
        (str(root / 'assistant_config.consumer.yml'), '.'),
        (str(root / 'assistant_config.consigliere.yml'), '.'),
        (str(root / 'assets'), 'assets'),
        (str(root / 'profiles'), 'profiles'),
    ] + _chroma_datas + _rust_datas,
    hiddenimports=[
        'modules.base_assistant',
        'modules.brain_backends.groq_backend',
        'modules.brain_backends.kobold_backend',
        'modules.brain_backends.venice_backend',
        'modules.brain_backends.gemini_backend',
        'modules.memory_vault.memory_manager',
        'modules.personality_engine.engine',
        'modules.gui.chat_app',
        'modules.gui.first_run',
        'modules.gui.startup_check',
        'modules.gui.voice_io',
        'modules.personality_engine.identity',
        'pyttsx3',
        'speech_recognition',
        'modules.consumer_bootstrap',
        'modules.arden_env',
        'modules.crash_log',
        'modules.consumer_smoke',
        'modules.arden_diagnose',
        'modules.arden_acceptance',
        'modules.memory_vault.sqlite_graph_store',
        'modules.memory_vault.memory_factory',
        'utils.embedding_utils',
        'chromadb',
        'chromadb.api.rust',
        'chromadb_rust_bindings',
        'chromadb.telemetry.product.posthog',
        'chromadb.telemetry.product.events',
        'posthog',
        'yaml',
        'dpath',
        'dotenv',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'modules.gui.splash',
        'modules.gui.sources_panel',
        'modules.gui.intake_choice',
        'modules.gui.intake_flow',
        'modules.gui.knowledge_panel',
        'modules.intake',
        'modules.intake.domains',
        'modules.intake.domain_packs',
        'modules.intake.engine',
        'modules.intake.facts_store',
        'modules.intake.progress',
        'modules.tactical_context',
        'modules.proactive',
        'modules.proactive.care',
        'modules.proactive.context_deepening',
        'modules.proactive.nudge',
        'modules.proactive.state',
        'modules.proactive.accountability',
        'modules.gui.tasks_panel',
        'modules.consigliere_acceptance',
        'modules.sources',
        'modules.sources.document_store',
        'modules.sources.ingest',
        'modules.sources.rag',
        'modules.gui.utilities_dialog',
        'modules.utilities',
        'modules.utilities.export_docx',
        'modules.utilities.email_draft',
        'modules.utilities.calendar_view',
        'docx',
        'modules.gui.arden_theme',
        'modules.gui.arden_decor',
        'modules.gui.arden_widgets',
        'modules.gui.session_store',
    ] + _chroma_hidden + _rust_hidden + collect_submodules('chromadb'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[str(root / 'packaging' / 'runtime_hook_arden.py')],
    excludes=[
        'realtimestt', 'RealtimeTTS', 'torch', 'torchvision', 'torchaudio',
        'tensorflow', 'jax', 'onnxruntime', 'elevenlabs',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Arden',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Arden',
)
