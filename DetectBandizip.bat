@echo off
rem  Copyright (c) 2026 bakeryg - MIT   github.com/bakeryg/archive-password-toolkit
setlocal EnableExtensions
chcp 65001 >nul 2>nul
title Bandizip detector - Archive Password Toolkit

echo ============================================================
echo   Bandizip detector
echo   for Archive Password Toolkit
echo ============================================================
echo.

set "FOUND="
set "BZPATH="

echo [1/5] common install folders
call :try "%ProgramFiles%\Bandizip\bz.exe"
call :try "%ProgramFiles(x86)%\Bandizip\bz.exe"
call :try "%ProgramW6432%\Bandizip\bz.exe"
call :try "%LOCALAPPDATA%\Bandizip\bz.exe"
call :try "%ProgramData%\Bandizip\bz.exe"
call :try "%~dp0bz.exe"
call :try "%~dp0Bandizip\bz.exe"
call :try "%~dp0..\bz.exe"

echo [2/5] PATH environment variable
for /f "delims=" %%p in ('where bz.exe 2^>nul') do call :try "%%p"

echo [3/5] registry (uninstall entries)
call :regscan "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
call :regscan "HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
call :regscan "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
call :regscan "HKLM\SOFTWARE\Bandizip"
call :regscan "HKCU\SOFTWARE\Bandizip"

echo [4/5] scanning drive roots (portable copies)
if defined BZPATH goto :skipscan
for %%d in (C D E F G H I J) do call :scanroot "%%d"
:skipscan

echo.
echo [5/5] RESULT
echo ------------------------------------------------------------
if not defined BZPATH goto :notfound

echo   FOUND:
echo     %BZPATH%
echo.
> "%~dp0bz_path.txt" echo %BZPATH%
echo   saved to bz_path.txt
echo   Archive Password Toolkit reads this file on startup.
echo.
echo ------------------------------------------------------------
echo   You can now run ArchivePasswordToolkit.exe
goto :end

:notfound
echo   NOT FOUND - could not locate Bandizip's bz.exe
echo ------------------------------------------------------------
echo.
echo   Please install Bandizip first (the free version is enough):
echo     https://www.bandisoft.com/bandizip/
echo     keeping the default install folder is easiest
echo.
echo   If you use a portable / green build:
echo     1) put the whole Bandizip folder next to this program, or
echo     2) create bz_path.txt containing one line:
echo        the full path of bz.exe
goto :end

:end
echo.
pause
endlocal
exit /b 0


rem ================= subroutines =================
rem Deliberately avoids  if ( ... )  blocks:
rem a "(x86)" inside a path would close the block early
rem and break the script.

:try
if defined BZPATH exit /b 0
if not exist %1 exit /b 0
set "BZPATH=%~f1"
echo        found: %~f1
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
