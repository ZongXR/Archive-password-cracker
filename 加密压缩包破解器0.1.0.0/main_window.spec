# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['main_window.py'],
             pathex=['C:\\Users\\DrZon\\PycharmProjects\\加密压缩包破解器'],
             binaries=[],
             datas=[('mainUI.ui', '.')],
             hiddenimports=['tools.py'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='main_window',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , version='version.txt', icon='icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='main_window')
