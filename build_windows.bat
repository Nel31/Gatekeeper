@echo off
echo ========================================
echo Building Gatekeeper for Windows
echo ========================================

REM Nettoyer les builds précédents
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

REM Activer l'environnement virtuel si disponible
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else if exist .venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM Installer/mettre à jour les dépendances
echo Installing/updating dependencies...
pip install -r requirements.txt

REM Créer l'exécutable avec PyInstaller
echo Building executable...
pyinstaller gatekeeper.spec --clean

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Build completed successfully!
    echo Executable location: dist\Gatekeeper.exe
    echo ========================================

    REM Créer un dossier de distribution avec tous les fichiers nécessaires
    echo Creating distribution folder...
    if not exist dist\Gatekeeper_Distribution mkdir dist\Gatekeeper_Distribution

    REM Copier l'exécutable
    copy dist\Gatekeeper.exe dist\Gatekeeper_Distribution\

    REM Créer un fichier README
    echo Creating README...
    (
        echo Certificateur de Comptes - Gatekeeper v2.0
        echo ==========================================
        echo.
        echo Pour lancer l'application, double-cliquez sur Gatekeeper.exe
        echo.
        echo Configuration requise:
        echo - Windows 7 ou supérieur
        echo - 4 GB de RAM minimum
        echo - 100 MB d'espace disque
        echo.
        echo En cas de problème, contactez le support technique.
    ) > dist\Gatekeeper_Distribution\README.txt

    echo.
    echo Distribution folder created: dist\Gatekeeper_Distribution
) else (
    echo.
    echo ========================================
    echo Build failed! Check the error messages above.
    echo ========================================
)

pause