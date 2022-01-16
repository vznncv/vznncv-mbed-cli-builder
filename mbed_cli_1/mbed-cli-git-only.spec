# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

import os
import sys
sys.path.append(os.getcwd())
import app_hook_utils
pkg_info = app_hook_utils.collect_package_data_from_requirements()

a = Analysis(['entry_point_git_only.py'],
             pathex=[],
             binaries=pkg_info['binaries'],
             datas=pkg_info['datas'],
             hiddenimports=pkg_info['hiddenimports'],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=app_hook_utils.collect_runtime_hooks(),
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
a = app_hook_utils.deduplicate_data(a)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='mbed-cli-git-only',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
