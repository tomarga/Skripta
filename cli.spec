# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['skripta-cli.py'],
             pathex=['venv/lib/python3.8/site-packages/', 'env.json', 'skripta', 'project.egg-info', 'skripta/resources'],
             binaries=[],
             datas=[],
             hiddenimports=['PyQt6'],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=['googleapiclient'],
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
          name='transkripta',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )

b = Analysis(['worker-cli.py'],
             pathex=['venv/lib/python3.8/site-packages/', 'env.json', 'skripta', 'project.egg-info', 'venv/lib/python3.8/site-packages/snowboy-1.3.0-py3.8.egg'],
             binaries=[],
             datas=[("env.json",'.'), ('venv/lib/python3.8/site-packages/google_api_python_client-1.8.0.dist-info', '.')],
             hiddenimports=['PyQt6', 'snowboy', 'googleapiclient'],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=['googleapiclient'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyzb = PYZ(b.pure, b.zipped_data,
             cipher=block_cipher)

exeb = EXE(pyzb,
          b.scripts,
          [],
          exclude_binaries=True,
          name='worker-cli',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )

coll = COLLECT(exe,
               exeb,
               a.binaries,
               a.zipfiles,
               a.datas,
               b.binaries,
               b.zipfiles,
               b.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='skripta')
