@echo off
chcp 65001 >nul
title 🥖 BakeryPro - Запуск
echo ========================================
echo           BAKERYPRO - СИСТЕМА
echo ========================================
echo.

:menu
echo [1] 🤖 Запустить Telegram бота
echo [2] 🖥️ Запустить менеджер заказов
echo [3] 📦 Установить зависимости
echo [4] 🚪 Выход
echo.
set /p choice="Выберите действие [1-4]: "

if "%choice%"=="1" goto start_bot
if "%choice%"=="2" goto start_manager
if "%choice%"=="3" goto install_deps
if "%choice%"=="4" goto exit

echo ❌ Неверный выбор!
timeout /t 2 >nul
goto menu

:start_bot
echo 🚀 Запускаем Telegram бота...
echo ⚠️ Для остановки нажмите Ctrl+C
echo.
python bot.py
goto menu

:start_manager
echo 🖥️ Запускаем менеджер заказов...
echo.
python manager.py
goto menu

:install_deps
echo 📦 Устанавливаем зависимости...
call install.bat
goto menu

:exit
echo 🥖 До свидания!
timeout /t 2 >nul
exit