@echo off
rem  Copyright (c) 2026 bakeryg - MIT   github.com/bakeryg/archive-password-toolkit
setlocal EnableExtensions
title Bandizip detector - Archive Password Toolkit

echo ============================================================
echo   Bandizip 检测工具  /  Bandizip detector
echo   给 Archive Password Toolkit 使用
echo ============================================================
echo.

set "FOUND="
set "BZPATH="

echo [1/5] 常见安装目录 / standard install folders
call :try "%ProgramFiles%\Bandizip\bz.exe"
call :try "%ProgramFiles(x86)%\Bandizip\bz.exe"
call :try "%ProgramW6432%\Bandizip\bz.exe"
call :try "%LOCALAPPDATA%\Bandizip\bz.exe"
call :try "%ProgramData%\Bandizip\bz.exe"
call :try "%~dp0bz.exe"
call :try "%~dp0Bandizip\bz.exe"
call :try "%~dp0..\bz.exe"

echo [2/5] 环境变量 PATH
for /f "delims=" %%p in ('where bz.exe 2^>nul') do call :try "%%p"

echo [3/5] 注册表 / registry
call :regscan "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
call :regscan "HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
call :regscan "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
call :regscan "HKLM\SOFTWARE\Bandizip"
call :regscan "HKCU\SOFTWARE\Bandizip"

echo [4/5] 扫描各盘查找便携版 / scanning drives
if defined BZPATH goto :skipscan
for %%d in (C D E F G H I J) do call :scanroot "%%d"
:skipscan

echo.
echo [5/5] 结果 / RESULT
echo ------------------------------------------------------------
if not defined BZPATH goto :notfound

echo   FOUND 找到:
echo     %BZPATH%
echo.
> "%~dp0bz_path.txt" echo %BZPATH%
echo   已写入 bz_path.txt   (saved to bz_path.txt)
echo   Archive Password Toolkit 启动时会自动读取它
echo.
echo ------------------------------------------------------------
echo   现在可以启动 ArchivePasswordToolkit.exe 了
goto :end

:notfound
echo   NOT FOUND 没有找到 Bandizip 的 bz.exe
echo ------------------------------------------------------------
echo.
echo   请先安装 Bandizip（免费版就够）:
echo     https://www.bandisoft.com/bandizip/
echo     安装时保持默认目录即可
echo.
echo   如果你用的是便携版 / 绿色版:
echo     1) 把 Bandizip 整个文件夹放到本程序旁边，或
echo     2) 新建一个 bz_path.txt，里面只写一行 bz.exe 的完整路径
echo.
echo   Please install Bandizip first, or write the full path of
echo   bz.exe into bz_path.txt next to this script.
goto :end

:end
echo.
pause
endlocal
exit /b 0


rem ================= 子过程 =================
rem 刻意不使用 if ( ... ) 括号块：
rem 路径里的 "(x86)" 会提前闭合括号，导致语法错误。

:try
if defined BZPATH exit /b 0
if not exist %1 exit /b 0
set "BZPATH=%~f1"
echo        找到 / found: %~f1
exit /b 0

:regscan
if defined BZPATH exit /b 0
for /f "tokens=2*" %%A in ('reg query "%~1" /s /f "Bandizip" 2^>nul ^| findstr /i "InstallLocation"') do call :try "%%B\bz.exe"
if defined BZPATH exit /b 0
for /f "tokens=2*" %%A in ('reg query "%~1" /s /f "Bandizip" 2^>nul ^| findstr /i "DisplayIcon"') do call :try "%%~dpB\bz.exe"
if defined BZPATH exit /b 0
for /f "tokens=2*" %%A in ('reg query "%~1" /s /f "Bandizip" 2^>nul ^| findstr /i "Path"') do call :try "%%B\bz.exe"
exit /b 0

:scanroot
if defined BZPATH exit /b 0
if not exist %1:\ exit /b 0
for /d %%f in ("%1:\*bandi*") do call :scandir "%%f"
for /d %%f in ("%1:\*") do call :scandir2 "%%f"
exit /b 0

:scandir
call :try "%~1\bz.exe"
for /d %%g in ("%~1\*") do call :try "%%g\bz.exe"
exit /b 0

:scandir2
call :try "%~1\bz.exe"
call :try "%~1\Bandizip\bz.exe"
exit /b 0
