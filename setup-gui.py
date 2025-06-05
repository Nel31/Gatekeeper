#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
setup_gui.py - Installation et configuration de l'interface graphique
"""

import subprocess
import sys
import os
from pathlib import Path


def create_requirements_gui():
    """Créer le fichier requirements pour l'interface graphique"""
    requirements = """# Requirements pour l'interface graphique
PySide6>=6.5.0
pandas>=1.5.0
openpyxl>=3.1.0
rapidfuzz>=3.0.0
pyyaml>=6.0
unidecode>=1.3.0

# Requirements originaux du projet
typer>=0.9.0
colorama>=0.4.6
"""
    
    with open("requirements_gui.txt", "w", encoding="utf-8") as f:
        f.write(requirements)
    
    print("✅ Fichier requirements_gui.txt créé")


def create_launcher_script():
    """Créer un script de lancement pour l'interface graphique"""
    
    # Script pour Windows
    bat_content = """@echo off
echo Lancement du Certificateur de Comptes...
python certificateur-gui.py
pause
"""
    
    with open("launch_gui.bat", "w", encoding="utf-8") as f:
        f.write(bat_content)
    
    # Script pour Linux/Mac
    sh_content = """#!/bin/bash
echo "Lancement du Certificateur de Comptes..."
python3 certificateur-gui.py
"""
    
    with open("launch_gui.sh", "w", encoding="utf-8") as f:
        f.write(sh_content)
    
    # Rendre le script exécutable sur Unix
    if sys.platform != "win32":
        os.chmod("launch_gui.sh", 0o755)
    
    print("✅ Scripts de lancement créés")


def create_desktop_entry():
    """Créer un raccourci bureau pour Linux"""
    desktop_content = """[Desktop Entry]
Version=1.0
Type=Application
Name=Certificateur de Comptes
Comment=Interface de certification des comptes utilisateurs
Exec=python3 /path/to/certificateur-gui.py
Icon=/path/to/icon.png
Terminal=false
Categories=Office;Utility;
"""
    
    with open("certificateur.desktop", "w", encoding="utf-8") as f:
        f.write(desktop_content)
    
    print("✅ Fichier .desktop créé (Linux)")


def create_pyinstaller_spec():
    """Créer un fichier spec pour PyInstaller"""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['certificateur-gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('*.csv', '.'),
        ('*.yml', '.'),
    ],
    hiddenimports=[
        'PySide6',
        'pandas',
        'openpyxl',
        'rapidfuzz',
        'pyyaml',
        'unidecode',
        'colorama',
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
    [],
    exclude_binaries=True,
    name='CertificateurComptes',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CertificateurComptes'
)
"""
    
    with open("certificateur-gui.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print("✅ Fichier spec PyInstaller créé")


def create_icon():
    """Créer une icône simple en Python (SVG)"""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="256" height="256" viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg">
    <rect width="256" height="256" rx="20" fill="#1e1e1e"/>
    <circle cx="128" cy="80" r="40" fill="#0d7377"/>
    <path d="M 70 150 Q 128 120 186 150 L 186 200 Q 128 220 70 200 Z" fill="#0d7377"/>
    <circle cx="180" cy="180" r="30" fill="#14a085"/>
    <path d="M 165 180 L 175 190 L 195 170" stroke="white" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""
    
    with open("icon.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    print("✅ Icône SVG créée")
    print("ℹ️  Pour Windows, convertissez icon.svg en icon.ico avec un outil en ligne")


def install_dependencies():
    """Installer les dépendances"""
    print("\n📦 Installation des dépendances...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements_gui.txt"
        ], check=True)
        print("✅ Dépendances installées avec succès")
    except subprocess.CalledProcessError:
        print("❌ Erreur lors de l'installation des dépendances")
        print("Essayez: pip install -r requirements_gui.txt")


def build_executable():
    """Construire l'exécutable avec PyInstaller"""
    print("\n🔨 Construction de l'exécutable...")
    
    try:
        # Installer PyInstaller si nécessaire
        subprocess.run([
            sys.executable, "-m", "pip", "install", "pyinstaller"
        ], check=True)
        
        # Construire l'exécutable
        subprocess.run([
            "pyinstaller", "certificateur-gui.spec", "--clean"
        ], check=True)
        
        print("✅ Exécutable créé dans le dossier 'dist'")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la construction: {e}")


def create_config_files():
    """Créer les fichiers de configuration par défaut"""
    # Créer le dossier config s'il n'existe pas
    Path("config").mkdir(exist_ok=True)
    
    # Vérifier si column_aliases.yml existe
    if not Path("config/column_aliases.yml").exists():
        print("⚠️  config/column_aliases.yml n'existe pas - création d'un fichier par défaut")
        default_config = """# Configuration des alias de colonnes
code_utilisateur:
  - Identifiant
  - CODE_UTILISATEUR

nom_prenom:
  - NomComplet
  - NOM_UTILISATEUR

profil:
  - Profil utilisateur
  - PROFIL

direction:
  - Direction
  - LIBELLE SERVICE

last_login:
  - DATE_DERNIÈRE_CONNEXION

status:
  - ACTIF
  - Statut

extraction_date:
  - DATE_EXTRACTION
"""
        with open("config/column_aliases.yml", "w", encoding="utf-8") as f:
            f.write(default_config)


def main():
    """Menu principal d'installation"""
    print("""
╔══════════════════════════════════════════════╗
║     Installation - Certificateur de Comptes   ║
║              Interface Graphique              ║
╚══════════════════════════════════════════════╝
    """)
    
    while True:
        print("\nQue souhaitez-vous faire ?")
        print("1. Installation complète")
        print("2. Créer les fichiers de configuration")
        print("3. Installer les dépendances uniquement")
        print("4. Créer l'exécutable Windows/Linux")
        print("5. Créer les scripts de lancement")
        print("0. Quitter")
        
        choice = input("\nVotre choix : ")
        
        if choice == "1":
            # Installation complète
            create_requirements_gui()
            create_config_files()
            install_dependencies()
            create_launcher_script()
            create_icon()
            create_desktop_entry()
            create_pyinstaller_spec()
            
            print("\n✅ Installation complète terminée!")
            print("\nPour lancer l'application:")
            print("- Windows: double-cliquez sur launch_gui.bat")
            print("- Linux/Mac: ./launch_gui.sh")
            
        elif choice == "2":
            create_config_files()
            
        elif choice == "3":
            create_requirements_gui()
            install_dependencies()
            
        elif choice == "4":
            create_pyinstaller_spec()
            build_executable()
            
        elif choice == "5":
            create_launcher_script()
            create_desktop_entry()
            
        elif choice == "0":
            print("\nAu revoir!")
            break
            
        else:
            print("❌ Choix invalide")


if __name__ == "__main__":
    main()
