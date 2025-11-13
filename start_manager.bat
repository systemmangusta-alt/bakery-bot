@echo off
chcp 65001 >nul
title 🥖 BakeryPro Manager - Золотая коллекция
echo ========================================
echo      МЕНЕДЖЕР BAKERYPRO - ЗАПУСК
echo ========================================
echo.

echo 🔍 Проверяем Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    echo 📥 Установите Python с python.org
    pause
    exit /b 1
)

echo ✅ Python найден

echo 🔍 Проверяем customtkinter...
python -c "import customtkinter" 2>nul
if errorlevel 1 (
    echo ❌ customtkinter не установлен!
    echo 📥 Запустите install.bat
    pause
    exit /b 1
)

echo ✅ customtkinter найден

echo 🎨 Запускаем менеджер в золотых тонах...
echo ⚠️  Закройте это окно для остановки
echo ========================================
echo.

cd /d "%~dp0"
python manager.py

if errorlevel 1 (
    echo.
    echo ❌ Ошибка запуска менеджера!
    echo 🔍 Проверьте файл manager.py
    echo.
    pause
)