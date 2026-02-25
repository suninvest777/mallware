# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

# Включаем config.json, если он существует
datas_list = [('embedded_image.jpg', '.')]
if os.path.exists('config.json'):
    datas_list.append(('config.json', '.'))

a = Analysis(
    ['dropper.py'],
    pathex=[],
    binaries=[],
    datas=datas_list,
    hiddenimports=['requests'],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='dropper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Без консоли - незаметный запуск
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Иконка отключена для упрощения сборки
)
