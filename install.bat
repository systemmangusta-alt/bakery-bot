@echo off
chcp 65001 >nul
title 🥖 BakeryPro - Установка
echo ========================================
echo           BAKERYPRO - УСТАНОВКА
echo ========================================
echo.

echo 🔍 Проверяем Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    echo.
    echo 📥 СКАЧАЙТЕ И УСТАНОВИТЕ Python:
    echo 🔗 https://www.python.org/downloads/
    echo.
    echo ⚠️ ВНИМАНИЕ при установке:
    echo ✅ Обязательно отметьте "Add Python to PATH"
    echo ✅ Нажмите "Install Now"
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set python_ver=%%i
echo ✅ Установлен: %python_ver%
echo.

echo 🔧 ПРОВЕРЯЕМ ДОСТУПНОСТЬ PIP...
echo ========================================
echo.

echo Способ 1: Пробуем python -m pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ python -m pip не работает
    echo.
    echo Способ 2: Пробуем pip напрямую...
    pip --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ pip не найден в системе!
        echo.
        echo 🔧 РЕШЕНИЕ ПРОБЛЕМЫ:
        echo 1. Переустановите Python
        echo 2. При установке ОБЯЗАТЕЛЬНО отметьte "Add Python to PATH"
        echo 3. Или добавьте Python в PATH вручную
        echo.
        echo 📍 Путь к Python обычно: C:\Users\ВАШЕ_ИМЯ\AppData\Local\Programs\Python\Python314\
        echo 📍 Путь к Scripts: C:\Users\ВАШЕ_ИМЯ\AppData\Local\Programs\Python\Python314\Scripts\
        echo.
        pause
        exit /b 1
    )
    echo ✅ pip доступен напрямую
    set PIP_CMD=pip
) else (
    echo ✅ python -m pip работает
    set PIP_CMD=python -m pip
)

echo.
echo 📦 УСТАНАВЛИВАЕМ БИБЛИОТЕКИ...
echo ========================================
echo.

echo 1. Устанавливаем telebot...
%PIP_CMD% install pytelegrambotapi
if errorlevel 1 (
    echo ❌ Ошибка установки telebot!
    echo.
    echo 🔧 Альтернативная установка...
    python -c "import os; os.system('pip install pytelegrambotapi')"
    if errorlevel 1 (
        echo ❌ Критическая ошибка установки!
        pause
        exit /b 1
    )
)
echo ✅ telebot установлен

echo.
echo 2. Устанавливаем customtkinter...
%PIP_CMD% install customtkinter
if errorlevel 1 (
    echo ❌ Ошибка установки customtkinter!
    python -c "import os; os.system('pip install customtkinter')"
)
echo ✅ customtkinter установлен

echo.
echo 3. Устанавливаем matplotlib для графиков...
%PIP_CMD% install matplotlib
if errorlevel 1 (
    echo ⚠️ Не удалось установить matplotlib, графики будут отключены
    echo 🔧 Альтернативная установка...
    python -c "import os; os.system('pip install matplotlib')"
)
echo ✅ matplotlib установлен

echo.
echo 4. Устанавливаем другие библиотеки...
%PIP_CMD% install requests pillow
echo ✅ Дополнительные библиотеки установлены

echo.
echo 📁 СОЗДАЕМ СТРУКТУРУ ПАПОК...
mkdir data 2>nul
mkdir logs 2>nul
echo ✅ Папки созданы

echo.
echo 🎉 УСТАНОВКА ЗАВЕРШЕНА!
echo ========================================
echo.
echo 🚀 ЧТО ДЕЛАТЬ ДАЛЬШЕ:
echo 1. Запустите start.bat для работы
echo 2. Выберите "Запустить Telegram бота"
echo.
echo 📝 КОНФИГУРАЦИЯ БОТА:
echo - Токен бота: 8125733355:AAE4a-XiC48YQ3FUNuIfY_HIGYAf56-iDaY
echo - ID администратора: 7631590101
echo.
pause