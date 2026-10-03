@echo off
rem  Copyright (c) 2026 bakeryg - MIT   github.com/bakeryg/archive-password-toolkit
rem ============================================================
rem  安装依赖.bat —— 一键安装 PySide6（本程序唯一需要装的东西）
rem
rem  用法：双击本文件，需要联网。
rem  另外还需要 Python 3.12 和 Bandizip，见 README。
rem ============================================================
setlocal EnableExtensions
cd /d "%~dp0"
title 安装依赖 - Archive Password Toolkit

echo ============================================================
echo   Archive Password Toolkit 依赖安装
echo ============================================================
echo.

set "PY="
py -3 -c "import sys" >nul 2>nul && set "PY=py -3"
if not defined PY python -c "import sys" >nul 2>nul && set "PY=python"
if not defined PY python3 -c "import sys" >nul 2>nul && set "PY=python3"

if not defined PY goto nopython

echo [1/3] 找到的 Python：
%PY% -c "import sys; print('      ' + sys.executable)"
%PY% -c "import sys; print('      版本 ' + sys.version.split()[0])"
echo.

echo [2/3] 检查 PySide6 ...
%PY% -c "import PySide6" >nul 2>nul
if not errorlevel 1 goto already

echo       尚未安装，开始下载安装（第一次可能要几分钟，请耐心等）
echo.
%PY% -m pip install PySide6
if errorlevel 1 (
  echo.
  echo       默认源失败，改用国内镜像重试 ...
  echo.
  %PY% -m pip install PySide6 -i https://pypi.tuna.tsinghua.edu.cn/simple
)
if errorlevel 1 goto failed

:already
echo.
echo [3/3] 验证 ...
%PY% -c "import PySide6; print('      PySide6 ' + PySide6.__version__ + ' 已就绪')"
if errorlevel 1 goto failed

echo.
echo ============================================================
echo   完成！现在可以双击 启动.bat 或 ArchivePasswordToolkit.exe
echo ============================================================
echo.
pause
exit /b 0

:nopython
echo [错误] 没有找到 Python。
echo.
echo 请先安装 Python 3.12：https://www.python.org/downloads/
echo 安装时务必勾选 Add python.exe to PATH，装完再双击本文件。
echo.
pause
exit /b 1

:failed
echo.
echo [错误] PySide6 安装失败，请检查网络后重试，或手动执行：
echo        py -3 -m pip install PySide6
echo.
pause
exit /b 1