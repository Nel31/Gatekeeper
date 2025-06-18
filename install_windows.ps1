# install_windows.ps1
# Script d'installation PowerShell corrige

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " CERTIFICATEUR DE COMPTES - GATEKEEPER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configurer l'encodage UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Verifier la politique d'execution
$executionPolicy = Get-ExecutionPolicy
if ($executionPolicy -eq "Restricted") {
    Write-Host "Configuration de la politique d'execution..." -ForegroundColor Yellow
    try {
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        Write-Host "OK - Politique d'execution configuree" -ForegroundColor Green
    }
    catch {
        Write-Host "ATTENTION - Impossible de modifier la politique d'execution" -ForegroundColor Red
        Write-Host "Executez PowerShell en tant qu'administrateur et relancez" -ForegroundColor Yellow
        Read-Host "Appuyez sur Entree pour continuer quand meme"
    }
}

# Verifier Python
Write-Host "Verification de Python..." -ForegroundColor Yellow
$pythonFound = $false
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK - Python detecte: $pythonVersion" -ForegroundColor Green
        $pythonFound = $true
    }
}
catch {
    # Ne rien faire, on va gerer ca plus bas
}

if (-not $pythonFound) {
    Write-Host "ERREUR - Python n'est pas installe ou non accessible" -ForegroundColor Red
    Write-Host ""
    Write-Host "Solutions:" -ForegroundColor Yellow
    Write-Host "1. Telechargez Python depuis: https://python.org" -ForegroundColor White
    Write-Host "2. Cochez 'Add Python to PATH' lors de l'installation" -ForegroundColor White
    Write-Host "3. Redemarrez PowerShell apres installation" -ForegroundColor White
    Write-Host ""
    Read-Host "Appuyez sur Entree pour quitter"
    exit 1
}

# Verifier si on est dans le bon repertoire
if (-not (Test-Path "requirements.txt")) {
    Write-Host "ERREUR - Fichier requirements.txt non trouve" -ForegroundColor Red
    Write-Host "Assurez-vous d'etre dans le repertoire du projet" -ForegroundColor Yellow
    Read-Host "Appuyez sur Entree pour quitter"
    exit 1
}

# Creer l'environnement virtuel
Write-Host "Creation de l'environnement virtuel..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "ATTENTION - Environnement virtuel existant detecte" -ForegroundColor Yellow
    $overwrite = Read-Host "Voulez-vous le recreer? (o/n)"
    if ($overwrite -eq "o" -or $overwrite -eq "O") {
        Remove-Item -Recurse -Force "venv"
        python -m venv venv
    }
} else {
    python -m venv venv
}

if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "ERREUR - Echec de creation de l'environnement virtuel" -ForegroundColor Red
    Read-Host "Appuyez sur Entree pour quitter"
    exit 1
}

Write-Host "OK - Environnement virtuel cree" -ForegroundColor Green

# Mettre a jour pip
Write-Host "Mise a jour de pip..." -ForegroundColor Yellow
& "venv\Scripts\python.exe" -m pip install --upgrade pip

# Installer les dependances
Write-Host "Installation des dependances..." -ForegroundColor Yellow
Write-Host "Cela peut prendre quelques minutes..." -ForegroundColor Gray

$installResult = & "venv\Scripts\pip.exe" install -r requirements.txt 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "OK - Dependances installees avec succes" -ForegroundColor Green
} else {
    Write-Host "ATTENTION - Problemes lors de l'installation:" -ForegroundColor Yellow
    Write-Host $installResult -ForegroundColor Red

    # Tentative de reparation PyQt6
    Write-Host "Tentative d'installation manuelle de PyQt6..." -ForegroundColor Yellow
    & "venv\Scripts\pip.exe" install PyQt6 --force-reinstall --no-cache-dir
}

# Creer les repertoires necessaires
Write-Host "Creation des repertoires..." -ForegroundColor Yellow
$dirs = @("data", "logs", "reports")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "OK - Repertoire $dir cree" -ForegroundColor Green
    }
}

# Test rapide PyQt6
Write-Host "Test de PyQt6..." -ForegroundColor Yellow
$pyqt6Test = & "venv\Scripts\python.exe" -c "import PyQt6.QtWidgets; print('PyQt6_OK')" 2>&1
if ($pyqt6Test -like "*PyQt6_OK*") {
    Write-Host "OK - PyQt6 fonctionne correctement" -ForegroundColor Green
} else {
    Write-Host "ATTENTION - Probleme avec PyQt6" -ForegroundColor Yellow
    Write-Host "L'application pourrait ne pas fonctionner correctement" -ForegroundColor Red
}

# Test des modules core
Write-Host "Test des modules de l'application..." -ForegroundColor Yellow
$modulesTest = & "venv\Scripts\python.exe" -c "from ui.main_window import CertificateurApp; print('Modules_OK')" 2>&1
if ($modulesTest -like "*Modules_OK*") {
    Write-Host "OK - Modules de l'application fonctionnent" -ForegroundColor Green
} else {
    Write-Host "ATTENTION - Probleme avec les modules de l'application" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "         INSTALLATION TERMINEE         " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Pour lancer l'application:" -ForegroundColor White
Write-Host "1. venv\Scripts\Activate.ps1" -ForegroundColor Green
Write-Host "2. python gui.py" -ForegroundColor Green

Write-Host ""
Write-Host "Ou utilisez:" -ForegroundColor White
Write-Host ".\launch_app.ps1" -ForegroundColor Green

Write-Host ""
Write-Host "Pour tester la compatibilite:" -ForegroundColor White
Write-Host "python test_windows_compatibility.py" -ForegroundColor Green

Write-Host ""
$launch = Read-Host "Voulez-vous lancer l'application maintenant? (o/n)"
if ($launch -eq "o" -or $launch -eq "O") {
    Write-Host "Lancement de l'application..." -ForegroundColor Green
    & "venv\Scripts\python.exe" gui.py
}

Write-Host ""
Write-Host "Installation terminee avec succes!" -ForegroundColor Green
Read-Host "Appuyez sur Entree pour quitter"