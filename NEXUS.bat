
@echo off
title NEXUS 1.0.0
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo ERRO: Ambiente Python do NEXUS nao encontrado.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" app.py

if errorlevel 1 (
    echo.
    echo O NEXUS foi encerrado com um erro.
    pause
)
