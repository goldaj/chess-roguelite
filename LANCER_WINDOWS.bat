@echo off
setlocal
cd /d "%~dp0"
title Chess Roguelite - Version test

echo.
echo ========================================
echo   CHESS ROGUELITE - VERSION DE TEST
echo ========================================
echo.
echo Mode Python (utilisable sans executable compile).
echo La partie de test ne remplace PAS la sauvegarde habituelle.
echo.

if exist ".venv-playtest\Scripts\python.exe" goto check_deps

echo Creation de l'environnement de test...
where py >nul 2>nul
if errorlevel 1 goto use_python
py -3 -m venv ".venv-playtest"
if not errorlevel 1 goto check_deps

:use_python
python -m venv ".venv-playtest"
if errorlevel 1 goto missing_python

:check_deps
if exist ".venv-playtest\.ready" goto launch
echo Premiere utilisation : installation de Pygame et Pillow...
".venv-playtest\Scripts\python.exe" -m pip install -r "requirements.txt"
if errorlevel 1 goto dependencies_error
echo installed>".venv-playtest\.ready"

:launch
echo Lancement du jeu...
".venv-playtest\Scripts\python.exe" "playtest_entry.py"
if errorlevel 1 goto failed
exit /b 0

:missing_python
echo ERREUR : Python 3 n'est pas installe, ou la creation de l'environnement a echoue.
echo Alternative sans Python : utiliser l'EXE depuis les artifacts GitHub Actions.
goto pause_error

:dependencies_error
echo ERREUR : impossible d'installer les dependances.
echo Verifier la connexion Internet et les messages ci-dessus.
goto pause_error

:failed
echo Le jeu a rencontre une erreur.
echo Voir la trace dans %%LOCALAPPDATA%%\ChessRoguelitePlaytest\last_crash.txt
goto pause_error

:pause_error
echo.
pause
exit /b 1
