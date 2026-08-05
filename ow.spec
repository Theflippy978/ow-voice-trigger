# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('icon.ico', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['QtNetwork', 'QtQml', 'QtQuick', 'QtSvg', 'QtXml', 'QtWebEngine', 'QtMultimedia', 'QtDBus', 'QtBluetooth', 'QtNfc', 'QtRemoteObjects'],
    noarchive=False,
    optimize=2,
)

excluded_dlls = ['opengl32sw.dll', 'Qt6Quick.dll', 'Qt6Qml.dll', 'Qt6QmlModels.dll', 'Qt6QmlMeta.dll', 'Qt6QmlWorkerScript.dll', 'Qt6Pdf.dll', 'Qt6OpenGL.dll', 'Qt6Network.dll']
a.binaries = [b for b in a.binaries if not any(excl in b[0] for excl in excluded_dlls)]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='OW\u8bed\u97f3\u89e6\u53d1\u5668',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)
