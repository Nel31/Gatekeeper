# requirements.txt
streamlit>=1.28.0
pandas>=1.5.0
openpyxl>=3.1.0
rapidfuzz>=3.0.0
typer>=0.9.0
colorama>=0.4.6
unidecode>=1.3.0
pyyaml>=6.0
pyinstaller>=5.13.0

# build_exe.py - Script de construction de l'exécutable
import subprocess
import sys
import shutil
from pathlib import Path

def build_executable():
    """Construction de l'exécutable avec PyInstaller"""
    
    # Commande PyInstaller
    cmd = [
        'pyinstaller',
        '--onefile',                    # Un seul fichier exécutable
        '--windowed',                   # Pas de console (optionnel)
        '--name=CertificateurComptes',  # Nom de l'exécutable
        '--icon=app_icon.ico',          # Icône (optionnel)
        '--add-data=config;config',     # Inclure le dossier config
        '--hidden-import=streamlit',
        '--hidden-import=pandas',
        '--hidden-import=openpyxl',
        '--hidden-import=rapidfuzz',
        '--hidden-import=unidecode',
        '--hidden-import=colorama',
        '--collect-all=streamlit',
        'app.py'                        # Script principal
    ]
    
    print("🔨 Construction de l'exécutable en cours...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Exécutable créé avec succès dans le dossier 'dist'")
        print("📁 Fichier: dist/CertificateurComptes.exe")
    else:
        print("❌ Erreur lors de la construction:")
        print(result.stderr)

def create_launcher():
    """Créer un script de lancement qui ouvre le navigateur automatiquement"""
    
    launcher_script = '''
import subprocess
import webbrowser
import time
import os
import sys
from threading import Timer

def open_browser():
    """Ouvre le navigateur après un délai"""
    time.sleep(3)  # Attendre que Streamlit démarre
    webbrowser.open('http://localhost:8501')

def main():
    # Démarrer Streamlit en arrière-plan
    print("🚀 Lancement du Certificateur de Comptes...")
    print("📱 L'interface va s'ouvrir dans votre navigateur...")
    
    # Ouvrir le navigateur après quelques secondes
    Timer(3.0, open_browser).start()
    
    # Lancer Streamlit
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 
            'app.py', 
            '--server.headless=true',
            '--server.port=8501',
            '--browser.gatherUsageStats=false'
        ], check=True)
    except KeyboardInterrupt:
        print("\\n👋 Application fermée.")
    except Exception as e:
        print(f"❌ Erreur : {e}")
        input("Appuyez sur Entrée pour fermer...")

if __name__ == "__main__":
    main()
'''
    
    with open('launcher.py', 'w', encoding='utf-8') as f:
        f.write(launcher_script)
    
    print("✅ Script de lancement créé: launcher.py")

def create_spec_file():
    """Créer un fichier .spec personnalisé pour PyInstaller"""
    
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
    ],
    hiddenimports=[
        'streamlit',
        'pandas',
        'openpyxl',
        'rapidfuzz',
        'unidecode',
        'colorama',
        'pyyaml',
        'typer'
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CertificateurComptes',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Gardez True pour voir les messages de Streamlit
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico'  # Optionnel
)
'''
    
    with open('app.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Fichier spec créé: app.spec")

def create_installer_batch():
    """Créer un fichier batch pour faciliter l'installation"""
    
    batch_content = '''@echo off
echo 🔨 Installation du Certificateur de Comptes
echo.

REM Créer les dossiers nécessaires
if not exist "config" mkdir config
if not exist "templates" mkdir templates

echo ✅ Dossiers créés

REM Copier les fichiers de configuration par défaut
echo # Configuration des alias de colonnes > config\\column_aliases.yml
echo # Ajoutez vos mappings de colonnes ici >> config\\column_aliases.yml

echo ✅ Configuration par défaut créée
echo.
echo 🎉 Installation terminée !
echo.
echo Pour lancer l'application, double-cliquez sur CertificateurComptes.exe
echo.
pause
'''
    
    with open('install.bat', 'w', encoding='utf-8') as f:
        f.write(batch_content)
    
    print("✅ Script d'installation créé: install.bat")

def main():
    """Script principal de construction"""
    print("🏗️  Configuration du déploiement Windows")
    print("=" * 50)
    
    # Créer les scripts utilitaires
    create_launcher()
    create_spec_file()
    create_installer_batch()
    
    print("\n🔧 Prêt pour la construction !")
    print("\nÉtapes suivantes:")
    print("1. Installez les dépendances: pip install -r requirements.txt")
    print("2. Construisez l'exécutable: python build_exe.py")
    print("3. Testez: dist/CertificateurComptes.exe")
    
    # Demander si on veut construire maintenant
    response = input("\n❓ Voulez-vous construire l'exécutable maintenant ? (o/n): ")
    if response.lower() in ['o', 'oui', 'y', 'yes']:
        build_executable()

if __name__ == "__main__":
    main()
