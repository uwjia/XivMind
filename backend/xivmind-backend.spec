# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

datas = [('app', 'app'), ('static', 'static'), ('skills', 'skills'), ('subagents', 'subagents')]
datas += collect_data_files('lancedb')
datas += collect_data_files('pyarrow')
datas += collect_data_files('sentence_transformers')
datas += collect_data_files('transformers')


a = Analysis(
    ['run_backend.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.auto', 'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto', 'uvicorn.protocols.websockets', 'uvicorn.protocols.websockets.auto', 'uvicorn.lifespan', 'uvicorn.lifespan.on', 'pydantic', 'pydantic_settings', 'loguru', 'httpx', 'aiofiles', 'aiosqlite', 'lancedb', 'pyarrow', 'sentence_transformers', 'transformers', 'torch', 'numpy', 'pandas'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['runtime_hook.py'],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='xivmind-backend',
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
    name='xivmind-backend',
)
