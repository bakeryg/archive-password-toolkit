@echo off
rem  Copyright (c) 2026 bakeryg - MIT   github.com/bakeryg/ArchivePasswordCracker
rem ============================================================
rem  启动.bat —— 启动 ArchivePasswordCracker
rem
rem  两个标签页：使用自定义字典（主内容） / 使用内置字典
rem  引擎：Bandizip 的 bz.exe
rem ============================================================
setlocal EnableExtensions
cd /d "%~dp0"
title ArchivePasswordCracker

set "PY="
py -3 -c "import sys" >nul 2>nul && set "PY=py -3"
if not defined PY python -c "import sys" >nul 2>nul && set "PY=python"

if not defined PY (
  echo [错误] 没有找到 Python，请先安装 Python 3.12 并勾选 Add python.exe to PATH。
  pause
  exit /b 1
)

%PY% -c "import PySide6" >nul 2>nul
if errorlevel 1 (
  echo [错误] 没有找到 PySide6，请先双击 安装依赖.bat 安装。
  pause
  exit /b 1
)

rem 优先用不弹黑框的解释器启动
set "PYW="
pyw -3 -c "import PySide6" >nul 2>nul && set "PYW=pyw -3"
if not defined PYW pythonw.exe -c "import PySide6" >nul 2>nul && set "PYW=pythonw.exe"

if defined PYW (
  start "" %PYW% "cracker312.py"
) else (
  %PY% "cracker312.py"
  if errorlevel 1 pause
)
endlocal