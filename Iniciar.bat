@echo off
title Automação de Cortes - Flask Server
echo Iniciando o ambiente virtual e o servidor Flask...
echo.

:: Vai para a pasta do projeto (caso o script seja executado de outro lugar)
cd /d "%~dp0"

:: Ativa o ambiente virtual (venv)
call venv\Scripts\activate.bat

:: Executa o aplicativo Python
python app.py

pause