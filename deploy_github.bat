@echo off
echo ==========================================
echo   DEPLOY PARA O GITHUB - DUELO DE ERAS
echo ==========================================
echo.
echo 1. Adicionando arquivos modificados...
git add app.py races.csv results.csv sprint_results.csv requirements.txt

echo.
echo 2. Criando commit...
git commit -m "Update: Dados completos da Temporada 2025 (Max 421 pts, Lewis 156 pts)"

echo.
echo 3. Enviando para o GitHub...
git push origin main

echo.
echo ==========================================
if %ERRORLEVEL% EQU 0 (
    echo   SUCESSO! As alteracoes foram enviadas.
) else (
    echo   ERRO! Verifique se voce esta logado no Git.
)
echo ==========================================
pause
