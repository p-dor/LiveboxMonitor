# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['../LiveboxMonitor.py'],
             pathex=['.'],
             binaries=[],
             datas=[ ('/usr/local/lib/python3.10/site-packages/certifi/cacert.pem', 'certifi') ],
             hiddenimports=['_cffi_backend'],
             hookspath=[],
             hooksconfig={},
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
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='LiveboxMonitor',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None)

app = BUNDLE(exe,
        name='LiveboxMonitor.app',
        icon='../../ico/LiveboxMonitor.ico',
        version='1.4')
