@echo off
chcp 65001 >nul
title 定时推送助手

echo.
echo ========================================
echo           定时推送助手
echo ========================================
echo.

echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python
    pause
    exit /b 1
)

echo ✅ Python环境正常

echo.
echo 正在检查依赖包...
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo ❌ tkinter不可用
    pause
    exit /b 1
)

python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo 正在安装requests...
    pip install requests
)



echo ✅ 依赖检查完成

echo.
echo 启动定时推送程序...
echo.

python cool_timer.py

echo.
echo 程序已退出
pause 