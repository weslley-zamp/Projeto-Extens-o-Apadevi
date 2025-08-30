# -*- mode: python ; coding: utf-8 -*-

block_cipher = None  # Adicionando esta linha que estava faltando

a = Analysis(
    ['main.py'],
    pathex=['C:\\Fontes\\Aplicacoes\\Projeto-Extens-o-Apadevi'],  # Adicionando o caminho absoluto
    binaries=[],
    datas=[
        ('words\\wordlist.txt', 'words'),  # Usando barras invertidas para Windows
        ('keyboard.ico', '.'),  # Corrigindo de .ico para .lco
        ('services\\*.py', 'services'),
        ('utils\\*.py', 'utils')
    ],
    hiddenimports=[
        'pynput.keyboard._win32',
        'services.word_generator',
        'services.tts_service',
        'utils.audio_player',
        'utils.comparator',
        'pygame',
        'gtts',
        'pyttsx3',
        'winsound'  # Adicionando winsound que é usado no código
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    bootloader_ignore_signals=False,
    debug=False,  # Mude para True
    strip=False,
    upx=False,  # Desative UPX para facilitar debugging
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='keyboard.ico'  # Adicione esta linha se quiser um ícone
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main'
)