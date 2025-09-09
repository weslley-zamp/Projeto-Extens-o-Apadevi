# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['C:\\Fontes\\Aplicacoes\\Projeto-Extens-o-Apadevi'],
    binaries=[],
    datas=[
        ('words\\wordlist.txt', 'words'),
        ('keyboard.ico', '.'),
        ('services', 'services'),
        ('utils', 'utils'),
        ('config.py', '.'), # Garante que o arquivo de configuração é incluído
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
        'winsound',
        'pynput.keyboard', # Adicione esta linha para garantir que o módulo principal seja importado
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='TypingGame', # Mude o nome do executável para algo mais descritivo
    bootloader_ignore_signals=False,
    debug=False,
    strip=False,
    upx=True, # Mantenha o UPX ativado para menor tamanho do arquivo final
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, # Mantenha em 'False' para o aplicativo não ter uma janela de console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='keyboard.ico'
)