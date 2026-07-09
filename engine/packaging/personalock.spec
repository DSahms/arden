# PyInstaller spec — PersonaLock Consumer Edition (skeleton)
# Build: pyinstaller packaging/personalock.spec
# Output: dist/PersonaLock/PersonaLock.exe

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules

root = Path(SPECPATH).parent

_chroma_datas, _chroma_binaries, _chroma_hidden = collect_all('chromadb')
_rust_datas, _rust_binaries, _rust_hidden = collect_all('chromadb_rust_bindings')

a = Analysis(
    [str(root / 'main_gui_assistant.py')],
    pathex=[str(root)],
    binaries=_chroma_binaries + _rust_binaries,
    datas=[
        (str(root / 'assistant_config.consumer.yml'), '.'),
        (str(root / 'assets'), 'assets'),
        (str(root / 'profiles'), 'profiles'),
    ] + _chroma_datas + _rust_datas,
    hiddenimports=[
        'modules.base_assistant',
        'modules.brain_backends.groq_backend',
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
        'modules.consumer_smoke',
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
    ] + _chroma_hidden + _rust_hidden + collect_submodules('chromadb'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[str(root / 'packaging' / 'runtime_hook_consumer.py')],
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
    name='PersonaLock',
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
    name='PersonaLock',
)
