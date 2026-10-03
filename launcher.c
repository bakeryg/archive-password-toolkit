/* ============================================================
 * launcher.c —— Archive Password Toolkit 启动壳（启动器源码）
 *
 * Copyright (c) 2026 bakeryg
 * SPDX-License-Identifier: MIT
 * 项目地址: https://github.com/bakeryg/archive-password-toolkit
 *
 * 编译（MinGW-w64）：
 *     windres icon.rc -O coff -o icon_res.o
 *     gcc -O2 -municode -mwindows -o ArchivePasswordToolkit.exe launcher.c icon_res.o
 *
 * 行为：
 *   1. 找脚本：<本目录>\cracker312\cracker312.py 优先；
 *      找不到就在本目录下找 cracker312.py（发布包是平铺结构，
 *      开发目录是 cracker312\ 子目录结构，两种都支持）。
 *   2. 找 Python：pythonw.exe 优先，其次 python.exe。
 *   3. 预检 PySide6（静默跑一次 python -c "import PySide6"）：
 *      缺库时给一句看得懂的提示，而不是双击后毫无反应。
 *   4. 用找到的 Python 启动脚本，工作目录设为脚本所在目录
 *      （这样 code.txt、icon.ico 都能就近找到）。
 *   5. 把压缩包拖到 exe 图标上时，以 --open <路径> 传给脚本。
 * ============================================================ */

#include <windows.h>
#include <wchar.h>

#define MSG_TITLE L"启动失败"

static int file_exists(const wchar_t *path)
{
    DWORD attr = GetFileAttributesW(path);
    return attr != INVALID_FILE_ATTRIBUTES && !(attr & FILE_ATTRIBUTE_DIRECTORY);
}

/* 去掉路径最后一段（得到所在目录），就地修改 */
static void strip_last(wchar_t *path)
{
    wchar_t *slash = wcsrchr(path, L'\\');
    if (slash) {
        *slash = 0;
    }
}

static void join_path(wchar_t *out, size_t cap, const wchar_t *dir, const wchar_t *name)
{
    _snwprintf(out, cap - 1, L"%s\\%s", dir, name);
    out[cap - 1] = 0;
}

/* 在 PATH 里找一个可用的 Python；pythonw.exe 优先（不弹黑框） */
static int find_python(wchar_t *out, size_t cap, int *is_windowed)
{
    static const wchar_t *names[2] = { L"pythonw.exe", L"python.exe" };
    int i;

    for (i = 0; i < 2; i++) {
        wchar_t full[MAX_PATH * 2];
        DWORD n = SearchPathW(NULL, names[i], NULL, MAX_PATH * 2, full, NULL);
        if (n > 0 && n < MAX_PATH * 2) {
            wcsncpy(out, full, cap - 1);
            out[cap - 1] = 0;
            *is_windowed = (i == 0);
            return 1;
        }
    }
    return 0;
}

/* 静默运行并等它结束，返回退出码；-1 表示根本没跑起来 */
static int run_wait(const wchar_t *cmd, const wchar_t *work)
{
    STARTUPINFOW si;
    PROCESS_INFORMATION pi;
    DWORD rc = (DWORD)-1;
    wchar_t buf[32768];

    wcsncpy(buf, cmd, 32767);
    buf[32767] = 0;

    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));

    if (!CreateProcessW(NULL, buf, NULL, NULL, FALSE,
                        CREATE_NO_WINDOW, NULL, work, &si, &pi)) {
        return -1;
    }
    WaitForSingleObject(pi.hProcess, 120000);
    GetExitCodeProcess(pi.hProcess, &rc);
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);
    return (int)rc;
}

/* 启动后不等待（GUI 程序要一直开着） */
static int run_detached(const wchar_t *cmd, const wchar_t *work)
{
    STARTUPINFOW si;
    PROCESS_INFORMATION pi;
    wchar_t buf[32768];

    wcsncpy(buf, cmd, 32767);
    buf[32767] = 0;

    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));

    if (!CreateProcessW(NULL, buf, NULL, NULL, FALSE, 0, NULL, work, &si, &pi)) {
        return 0;
    }
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);
    return 1;
}

/* 拖到 exe 上的文件：命令原样带引号，去掉首尾空白和成对的引号 */
static void clean_target(wchar_t *dst, size_t cap, const wchar_t *src)
{
    size_t len;

    if (!src) {
        dst[0] = 0;
        return;
    }
    while (*src == L' ' || *src == L'\t' || *src == L'"') {
        src++;
    }
    wcsncpy(dst, src, cap - 1);
    dst[cap - 1] = 0;

    len = wcslen(dst);
    while (len > 0 && (dst[len - 1] == L' ' || dst[len - 1] == L'\t' ||
                       dst[len - 1] == L'"')) {
        dst[--len] = 0;
    }
}

int WINAPI wWinMain(HINSTANCE hInst, HINSTANCE hPrev, PWSTR cmdLine, int nShow)
{
    wchar_t exe[MAX_PATH];
    wchar_t dir[MAX_PATH];
    wchar_t script[MAX_PATH * 2];
    wchar_t work[MAX_PATH * 2];
    wchar_t py[MAX_PATH * 2];
    wchar_t target[MAX_PATH * 2];
    wchar_t cmd[32768];
    int is_windowed = 0;

    (void)hInst;
    (void)hPrev;
    (void)nShow;

    if (!GetModuleFileNameW(NULL, exe, MAX_PATH)) {
        return 1;
    }
    wcsncpy(dir, exe, MAX_PATH - 1);
    dir[MAX_PATH - 1] = 0;
    strip_last(dir);

    /* 1) 找脚本：子目录优先，其次平铺 */
    join_path(script, MAX_PATH * 2, dir, L"cracker312\\cracker312.py");
    if (!file_exists(script)) {
        join_path(script, MAX_PATH * 2, dir, L"cracker312.py");
    }
    if (!file_exists(script)) {
        MessageBoxW(NULL,
                    L"找不到 cracker312.py\n"
                    L"请确认它和本程序在同一个文件夹（或 cracker312 子文件夹）里。",
                    MSG_TITLE, MB_ICONERROR);
        return 1;
    }

    /* 工作目录 = 脚本所在目录 */
    wcsncpy(work, script, MAX_PATH * 2 - 1);
    work[MAX_PATH * 2 - 1] = 0;
    strip_last(work);

    /* 2) 找 Python */
    if (!find_python(py, MAX_PATH * 2, &is_windowed)) {
        MessageBoxW(NULL,
                    L"没有找到 Python（pythonw.exe / python.exe）。\n\n"
                    L"本程序需要已安装 Python 3.12 和 PySide6。\n"
                    L"装好 Python 后，双击 安装依赖.bat 即可补上 PySide6。",
                    MSG_TITLE, MB_ICONERROR);
        return 1;
    }

    /* 3) 预检 PySide6 —— 避免 pythonw 无控制台时静默失败 */
    _snwprintf(cmd, 32767, L"\"%s\" -c \"import PySide6\"", py);
    cmd[32767] = 0;
    if (run_wait(cmd, work) != 0) {
        MessageBoxW(NULL,
                    L"没有找到 PySide6，或本机 Python 环境不可用。\n\n"
                    L"解决办法（任选其一）：\n"
                    L"  · 双击本目录下的 安装依赖.bat\n"
                    L"  · 命令行执行：pip install PySide6",
                    MSG_TITLE, MB_ICONERROR);
        return 1;
    }

    /* 4) 启动（拖入文件时带 --open） */
    clean_target(target, MAX_PATH * 2, cmdLine);
    if (target[0]) {
        _snwprintf(cmd, 32767, L"\"%s\" \"%s\" --open \"%s\"", py, script, target);
    } else {
        _snwprintf(cmd, 32767, L"\"%s\" \"%s\"", py, script);
    }
    cmd[32767] = 0;

    if (!run_detached(cmd, work)) {
        MessageBoxW(NULL,
                    L"无法启动 Python。\n请确认 安装依赖.bat 已经成功执行过。",
                    MSG_TITLE, MB_ICONERROR);
        return 1;
    }
    return 0;
}
