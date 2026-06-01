# -*- mode: python ; coding: utf-8 -*-
import os
import sys
import site

block_cipher = None

# Dynamically find spellchecker resources (works on any machine)
spellchecker_path = None
try:
    import spellchecker
    spellchecker_path = os.path.dirname(spellchecker.__file__)
except ImportError:
    # Fallback: try to find it in site-packages
    for site_path in site.getsitepackages():
        potential_path = os.path.join(site_path, 'spellchecker')
        if os.path.exists(potential_path):
            spellchecker_path = potential_path
            break

datas = [('icon.ico', '.')]
if spellchecker_path:
    resources_path = os.path.join(spellchecker_path, 'resources')
    if os.path.exists(resources_path):
        datas.append((resources_path, 'spellchecker/resources'))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'spellchecker',
        'spellchecker.spellchecker',
        'spellchecker.utils',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Notepad minus',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    codesign_entitlements_file=None,
    icon='icon.ico',
    version_file='version.txt',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Notepad minus',
)
