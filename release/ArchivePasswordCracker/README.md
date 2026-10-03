# ArchivePasswordCracker

**English** | [中文](#中文说明)

**Author: [bakeryg](https://github.com/bakeryg)** · MIT licensed · attribution in [`AUTHORS.md`](AUTHORS.md)

Recover a forgotten password for an encrypted archive — **pick a dictionary, then drag an
archive in**.

The cracking engine is the [Bandizip](https://www.bandisoft.com/bandizip/) command-line
tool `bz.exe`; the GUI is written in **Python 3.12 + PySide6**.

Supported formats: `zip` / `zipx` / `rar` / `7z` / `iso` / `tar` / `gz` / `bz2` / `xz`
(depending on your Bandizip build).

---

## Features

**Dictionary-based, drag-and-drop first.** The main workflow is: pick a wordlist, then
drag an archive in. The **Enumeration** tab is there as a fallback.

Two tabs — the first one opens by default:

| Tab | What it does |
|---|---|
| **Custom dictionary** ← main | Pick a `.txt` wordlist (encoding auto-detected: **UTF-8 / GBK**, so Chinese and non-ASCII passwords work, e.g. `ღ特殊符号示例ღ`), and **drop an archive into the box below** to start cracking with it. `选择字典...` switches the wordlist; `历史字典 ▾` lists the wordlists you used before (up to 15, most recent first). Dropping a `.txt` switches the wordlist instead of cracking. |
| **Enumeration** ← fallback | Tick the character sets (digits / lowercase / uppercase / symbols) and a length range — it enumerates the combinations and tries them one by one, no file needed. You can also **export the generated list** to a `.txt`.

Other niceties:

- You can also **drop an archive onto `ArchivePasswordCracker.exe` itself**
- Multi-threaded (thread count is adjustable in the UI)
- Live progress bar; stops on the first hit and shows the password
- Optional automatic extraction once the password is found
- The cracking engine never extracts while guessing — it only runs an integrity test,
  so wrong passwords fail in ~10–30 ms

---

## Requirements

| | |
|---|---|
| OS | Windows 10 / 11 (64-bit) |
| Python | **3.12**, available on `PATH` |
| PySide6 | `pip install -r requirements.txt` — or just double-click `安装依赖.bat` |
| Bandizip | installed (the tool looks for `bz.exe` in the usual install folders) |

> `ArchivePasswordCracker.exe` is a small **launcher** (under 100 KB). It starts
> `cracker312.py` with your installed Python, which keeps the download tiny and easy to
> update. Before starting it checks Python and PySide6 and tells you exactly what to
> install — no more double-click-and-nothing-happens. If you want a fully self-contained
> binary, package it yourself with PyInstaller.

### Can't find Bandizip?

The program locates `bz.exe` in this order:

1. `bz_path.txt` (a one-line file next to the program — see below)
2. the usual install folders (`C:\Program Files\Bandizip`, `C:\Program Files (x86)\Bandizip`)
3. your `PATH`

If you use a **portable / green build** of Bandizip (unzipped somewhere instead of
installed), the automatic lookup will not find it. Just run one of the detector scripts
(double-click it):

| Script | Language |
|---|---|
| `DetectBandizip.bat` | English |
| `检测Bandizip.bat` | 中文 |

Either one searches the standard folders, the registry, `PATH`, and scans drive roots for
a folder whose name contains `bandi`, then writes the result to `bz_path.txt`. The
application reads that file on startup — no restart needed if the app is already open, it
re-checks when you hit *Start*.

Alternatively, create `bz_path.txt` yourself containing a single line: the full path of
`bz.exe`.

---

## Usage

### GUI

1. Run **`ArchivePasswordCracker.exe`** (or `启动.bat`).
2. You land on the **Custom dictionary** tab (the main one):
   - pick a `.txt` with `选择字典...`, or reuse one from `历史字典 ▾`
   - **drop the archive onto the blue box** — it starts cracking with that wordlist
   - (clicking the blue box opens a file dialog instead)
3. To brute-force instead: switch to the **Enumeration** tab, tick character sets and a
   length range, then go straight to *Start* (or *Export dictionary* first).
4. Optionally choose an extraction folder (leave it empty to only display the password).
5. Click **Start**.

### Working directory (keep it off your system drive)

Everything the program writes — the dictionary history, its cache and its **temporary
files** — goes into one *working directory*. By default that is the program's own folder,
so the whole thing stays portable: copy the folder anywhere, including a USB stick, and it
keeps working.

To put it somewhere else (for example on `D:` so nothing lands on your system drive):

**Menu → 设置 (Settings) → 选择工作目录...** and pick a folder, e.g. `D:\APC_data`.
The dictionary history is carried over, and `TMP`/`TEMP` are redirected there too, so even
the processes the tool spawns stop writing to the system drive.

The other two menu entries are *打开工作目录* (open it in Explorer) and *恢复为程序目录*
(back to the default). Your choice is remembered in `config.json` next to the program —
that one small file always stays with the program, which is what makes the folder
portable.

### Dictionary file format

Plain text, **one password per line**:

```
123456
password
中文密码示例123
ღ特殊符号示例ღ
```

- Leading/trailing whitespace is stripped automatically.
- Lines starting with `#` are treated as comments and skipped.
- Encoding is auto-detected (UTF-8 / GBK), so Chinese passwords need no conversion.

### Command line (optional)

A pure CLI version, `bz_crack.py`, is included:

```bat
python bz_crack.py -a "D:\test.zip" -d "dict.txt" -t 8
python bz_crack.py -a "D:\test.zip" -d "dict.txt" --extract "D:\out"
python bz_crack.py -a "D:\test.zip" -d "dict.txt" --skip 10000 --limit 5000
```

Useful flags: `-t` threads, `--extract` extract on success, `--skip` / `--limit` to
resume a long run, `--pw-out` to choose where the found password is recorded,
`--no-pw-file` to not write it at all.

---

## Layout

```
ArchivePasswordCracker\
├── ArchivePasswordCracker.exe   # launcher - double-click this
├── cracker312.py                # GUI application (Python 3.12 + PySide6)
├── ui_mainwindow.py             # generated from UI/MainWindow.ui
├── ui_aboutdialog.py            # generated from UI/AboutDialog.ui
├── bz_crack.py                  # command-line version
├── zipprobe.py                  # in-process ZIP password pre-filter
├── icon.ico                     # application icon
├── 安装依赖.bat                  # one-click PySide6 installer
├── 启动.bat                     # alternative launcher (no console window)
├── DetectBandizip.bat           # Bandizip detector (English, for portable installs)
├── 检测Bandizip.bat              # Bandizip detector (Chinese)
├── code.txt                     # starter dictionary
├── requirements.txt
├── LICENSE
├── AUTHORS.md
└── README.md
```

The launcher source (`launcher.c`, `icon.rc`, `make_icon.py`) ships in the **source pack**,
not in this download. To rebuild it (requires MinGW-w64):

```bat
windres icon.rc -O coff -o icon_res.o
gcc -O2 -municode -mwindows -o ArchivePasswordCracker.exe launcher.c icon_res.o
```

---

## How it works

There are two stages. **For ZIP archives** the candidates are checked **in-process** —
no subprocess at all (`zipprobe.py`):

- **ZipCrypto** (what Bandizip / WinRAR use for `.zip`): the password is validated by
  decrypting the entry's 12-byte encryption header and comparing one check byte; if that
  passes, the following bytes are decrypted and fed to a raw inflate, so a wrong password
  is rejected in microseconds.
- **WinZip AES**: the 2-byte password verifier (PBKDF2-HMAC-SHA1, 1000 rounds) is compared.

Only the very few candidates that survive this pre-filter are handed to **Bandizip**,
which remains the final authority:

```bat
bz.exe t -p:<password> -y <archive>
```

| Exit code | Meaning |
|---|---|
| `0` | password correct (`All OK`) |
| `14` | wrong password (`Invalid Password`) |
| `15` | password required (`Password is needed`) |

Anything that is not a ZIP (RAR, 7z, …) sends every candidate straight to `bz.exe`,
exactly as before, and if the ZIP structure cannot be parsed the fast path disables
itself automatically.

### Performance

Measured on Windows 11, one file kept small, 1 MB deflate ZIP:

| | value |
|---|---|
| `bz.exe` per candidate | ~20 ms |
| in-process ZIP pre-filter | ~6 µs |
| **1,000,000-line dictionary, password on line 500,000** | **4.6 s** (108,000 candidates/s) |
| the same job through `bz.exe` | ~2500 s |
| resident memory added while streaming that dictionary | **~5 MB** |

Two things make this possible:

- The dictionary is **streamed line by line** — never loaded as a list (a list would cost
  ~75 bytes per entry, i.e. **0.7 GB for 10 million lines**).
- On the fast path the work is CPU-bound, so it runs in a **process pool** (threads would
  serialise on the GIL). If spawning processes is unavailable it degrades automatically to
  a single-threaded in-process scan, and finally to the `bz.exe` path.

---

## Limitations

- Requires Bandizip to be installed — without `bz.exe` nothing can be cracked.
- RAR limits passwords to roughly 127 characters (a RAR format limitation); ZIP has no
  such limit.
- Long, complex passwords (8+ characters mixing several character classes) cannot be
  brute-forced in practice — use a dictionary.

---

## Disclaimer

This tool is intended **only** for recovering passwords of your **own** archives.
Do not use it against files that are not yours.

---

## Author

**bakeryg** — <https://github.com/bakeryg/ArchivePasswordCracker>

MIT licensed; the copyright notice is in [`LICENSE`](LICENSE), and the complete attribution
(including upstream credits) in [`AUTHORS.md`](AUTHORS.md).

### Verifying an official release

Only builds published from the repository above are official. To check what you downloaded:

1. **Signed tag** — releases are tagged (`v1.0.0`) and the tag is **signed**, so GitHub shows
   a *Verified* badge next to it. An unsigned tag, or one whose signature does not verify,
   is not from the author.
2. **SHA256** — compare the file you downloaded with the value in the release notes:

   ```bat
   certutil -hashfile ArchivePasswordCracker.zip SHA256
   ```

3. **Commit history** — every commit is tied to the author's account and timestamped by
   GitHub, and predates any copy of this code found elsewhere.

> A "release" that claims to be this project but does not come from
> `github.com/bakeryg/ArchivePasswordCracker` should be treated as unreviewed third-party code.

## Credits

- The interface (`ui_mainwindow.py` / `ui_aboutdialog.py`) was generated from the Qt
  Designer `.ui` files of
  [GoogleLLP/Archive-password-cracker](https://github.com/GoogleLLP/Archive-password-cracker).
- Cracking engine: the [Bandizip](https://www.bandisoft.com/bandizip/) command-line tool.

---

# 中文说明

[English](#archivepasswordcracker) | **中文**

**作者：[bakeryg](https://github.com/bakeryg)** · MIT 许可 · 署名与第三方来源见 [`AUTHORS.md`](AUTHORS.md)

找回你忘记的压缩包密码 —— **选好字典，把压缩包拖进来就行**。

破解引擎使用 [Bandizip](https://www.bandisoft.com/bandizip/) 的命令行工具 `bz.exe`；
界面用 **Python 3.12 + PySide6** 编写。

支持的格式：`zip` / `zipx` / `rar` / `7z` / `iso` / `tar` / `gz` / `bz2` / `xz`
（取决于你本机 Bandizip 的版本）。

---

## 特性

**主打「字典 + 拖入」**：正常用法就是先选好字典，然后把压缩包拖进来。
内置的暴力枚举只作为兜底手段保留。

就两个标签页，默认打开第一个：

| 标签页 | 说明 |
|---|---|
| **使用自定义字典** ← 主内容 | 选一个 `.txt` 字典（自动识别 **UTF-8 / GBK** 编码，中文密码、`ღ特殊符号示例ღ` 这类字符都能正常读），然后**把压缩包拖进下面的框**即开始破解。`选择字典...` 换字典；`历史字典 ▾` 列出以前用过的字典（最多 15 个，最近用的排最前）。把 `.txt` 拖进来则是**换字典**，不算破解目标。 |
| **枚举破解** | 勾选字符集（数字 / 小写字母 / 大写字母 / 特殊符号）+ 设置位数范围，程序**边枚举边逐个试**（不用先生成文件）；也可以把枚举结果**导出成 `.txt` 字典**备用。 |

其它：

- 也可以直接把压缩包**拖到 `ArchivePasswordCracker.exe` 图标上**
- 多线程并发（界面上的「使用核心数量」可调）
- 进度条实时显示，命中即停并显示密码
- 命中后可选自动解压到指定目录
- 猜密码时只做完整性测试、不解压，所以**错误密码十几毫秒就被否掉**

---

## 运行环境

| 项目 | 要求 |
|---|---|
| 系统 | Windows 10 / 11（64 位） |
| Python | **3.12**，且已加入 `PATH` |
| PySide6 | `pip install -r requirements.txt`，或者直接双击 `安装依赖.bat` |
| Bandizip | 已安装（程序会在常见安装目录里找 `bz.exe`） |

> `ArchivePasswordCracker.exe` 是一个小体积**启动器**（不到 100 KB），它负责调用你本机的
> Python 去运行 `cracker312.py`。这样下载体积小、更新也方便；启动前它会先检查 Python 和
> PySide6，缺什么就直接告诉你装什么，不会出现双击了没反应的情况。
> 如果你想要完全独立的单体 exe，可以自己用 PyInstaller 打包。

### 找不到 Bandizip 怎么办？

程序按这个顺序找 `bz.exe`：

1. `bz_path.txt`（程序旁边的一个单行文件，见下）
2. 常见安装目录（`C:\Program Files\Bandizip`、`C:\Program Files (x86)\Bandizip`）
3. 系统 `PATH`

如果你用的是 **便携版 / 绿色版**（解压到某个盘、没走安装程序），自动查找是找不到的。
这时候**双击运行下面任意一个检测脚本**就行：

| 脚本 | 语言 |
|---|---|
| `检测Bandizip.bat` | 中文 |
| `DetectBandizip.bat` | English |

它会依次查标准目录、注册表、`PATH`，并扫描各盘根目录下名字含 `bandi` 的文件夹，
找到后把结果写进 `bz_path.txt`。程序启动时会读这个文件；
**如果程序已经开着也不用重启**，点「开始破解」时会重新检测。

也可以自己新建 `bz_path.txt`，里面只写一行 `bz.exe` 的完整路径。

---

## 使用方法

### 图形界面

1. 双击 **`ArchivePasswordCracker.exe`**（或 `启动.bat`）
2. 默认就在「**使用自定义字典**」页（主内容）：
   - 用 `选择字典...` 挑一个 `.txt`（或从 `历史字典 ▾` 里选以前用过的）
   - **把压缩包拖进那个蓝框** —— 自动用上面这本字典开始破解
   - （也可以点一下蓝框用文件对话框选压缩包）
3. 想改用穷举：切到「**枚举破解**」页，勾字符集、设位数，直接「开始破解」（也可以先「导出字典」）
4. 可选：选一个解压位置（留空则只显示密码、不解压）

### 工作目录（把文件挪出系统盘）

程序写的所有东西 —— 字典历史、缓存、**临时文件** —— 都放在一个「工作目录」里。
默认就是**程序自己的目录**，所以整个文件夹是绿色的：拷到任何地方（含 U 盘）都能直接用。

想换到别的盘（比如 `D:`，免得往系统盘写东西）：

**菜单 → 设置 → 选择工作目录...** 选一个目录，例如 `D:\APC_data`。
原有的字典历史会自动带过去，同时 `TMP`/`TEMP` 也指向那里 ——
连程序拉起来的子进程都不会再往系统盘写临时文件。

另外两项是 *打开工作目录*（用资源管理器打开）和 *恢复为程序目录*（回到默认）。
你的选择记在程序旁边的 `config.json` 里 —— 只有这一个小文件永远跟着程序走，
这也是整个文件夹能「拷走即用」的原因。

### 字典文件格式

纯文本，**一行一个密码**：

```
123456
password
中文密码示例123
ღ特殊符号示例ღ
```

- 行首行尾的空白会被自动去掉
- 以 `#` 开头的行视为注释，会被跳过
- 编码自动识别（UTF-8 / GBK），中文密码无需转换

### 命令行（可选）

包里附带了纯命令行版本 `bz_crack.py`：

```bat
python bz_crack.py -a "D:\test.zip" -d "dict.txt" -t 8
python bz_crack.py -a "D:\test.zip" -d "dict.txt" --extract "D:\out"
python bz_crack.py -a "D:\test.zip" -d "dict.txt" --skip 10000 --limit 5000
```

常用参数：`-t` 线程数、`--extract` 命中后解压、`--skip` / `--limit` 断点续跑、
`--pw-out` 指定密码记录位置、`--no-pw-file` 完全不写文件。

---

## 目录结构

```
ArchivePasswordCracker\
├── cracker312.py                # 图形界面主程序（Python 3.12 + PySide6）
├── ui_mainwindow.py             # 由 UI/MainWindow.ui 转换而来
├── ui_aboutdialog.py            # 由 UI/AboutDialog.ui 转换而来
├── bz_crack.py                  # 命令行版本
├── zipprobe.py                  # 进程内 zip 密码预筛（性能关键）
├── launcher.c                   # 启动壳源码
├── icon.rc                      # 图标资源脚本
├── icon.ico                     # 图标
├── make_icon.py                 # 生成 icon.ico 的脚本
├── 安装依赖.bat                  # 一键安装 PySide6
├── 启动.bat                     # 另一种启动方式（不弹黑框）
├── 检测Bandizip.bat              # Bandizip 检测工具（中文）
├── DetectBandizip.bat           # Bandizip detector (English)
├── code.txt                     # 起始字典
├── requirements.txt
├── LICENSE
├── AUTHORS.md
├── .gitignore
└── README.md
```

编译出来的 `ArchivePasswordCracker.exe` 不打进源码包，它作为 Release 附件发布。
重新编译启动器（需要 MinGW-w64）：

```bat
windres icon.rc -O coff -o icon_res.o
gcc -O2 -municode -mwindows -o ArchivePasswordCracker.exe launcher.c icon_res.o
```

---

## 工作原理

分两级。**对 zip 压缩包**，候选密码先在**进程内**校验，根本不起子进程（`zipprobe.py`）：

- **ZipCrypto**（Bandizip / WinRAR 的 zip 默认加密）：用密码解出条目的 12 字节加密头，
  比对其中一个校验字节；通过后再解密紧随其后的字节并尝试 inflate —— 错误密码**几微秒**就被否掉。
- **WinZip AES**：比对 2 字节密码校验值（PBKDF2-HMAC-SHA1，1000 轮）。

只有极少数通过预筛的候选，才交给 **Bandizip** 做最终确认：

```bat
bz.exe t -p:<密码> -y <压缩包>
```

| 退出码 | 含义 |
|---|---|
| `0` | 密码正确（`All OK`） |
| `14` | 密码错误（`Invalid Password`） |
| `15` | 需要密码（`Password is needed`） |

非 zip（rar / 7z 等）的每个候选仍然直接走 `bz.exe`，和以前完全一样；
zip 结构解析不出来时，快速路径会自动关闭并回落。

### 性能

在 Windows 11 上实测（1 MB 的 deflate zip）：

| 项目 | 数值 |
|---|---|
| `bz.exe` 每个候选 | 约 20 毫秒 |
| 进程内 zip 预筛 | 约 6 微秒 |
| **100 万行字典，正确密码在第 50 万行** | **4.6 秒**（10.8 万候选/秒） |
| 同样工作量走 `bz.exe` | 约 2500 秒 |
| 流式读取该字典时的常驻内存增量 | **约 5 MB** |

两个关键点：

- 字典是**逐行流式读取**的，从不整表载入 —— 整表要按每条约 75 字节算，
  **1000 万条就是 0.7 GB**。
- 快速路径是 CPU 密集的，所以跑在**多进程池**里（用线程会被 GIL 串行化）；
  如果多进程创建不了，会自动降级为单线程进程内扫描，最后才回落到 `bz.exe`。

---

## 已知限制

- 依赖本机安装的 Bandizip —— 没有 `bz.exe` 就破不了
- RAR 的密码长度上限约 127 字符（RAR 格式本身的限制），ZIP 无此限制
- 长且复杂的密码（8 位以上、多种字符集混合）靠枚举基本不可能，只能靠字典

---

## 免责声明

本工具仅用于**找回自己忘记的压缩包密码**。
请勿用于破解他人文件。

---

## 作者

**bakeryg** — <https://github.com/bakeryg/ArchivePasswordCracker>

MIT 许可，版权声明在 [`LICENSE`](LICENSE)，完整的署名与第三方来源在 [`AUTHORS.md`](AUTHORS.md)。

### 如何验证这是官方发布

只有从上面这个仓库发布出来的才算官方版本。拿到文件后可以这样核对：

1. **签名标签（最硬的一条）** —— 每个版本都打了标签（如 `v1.0.0`）并且**带签名**，GitHub 会在标签旁显示 *Verified* 徽章。没有徽章、或签名验证不通过的，不是作者发布的。
2. **SHA256** —— 和你下载到的文件比对（校验值写在 Release 说明里）：

   ```bat
   certutil -hashfile ArchivePasswordCracker.zip SHA256
   ```

3. **提交记录** —— 每一笔提交都绑定作者账号、时间由 GitHub 服务器记录，早于任何别处的副本。

> 如果你手上的渠道声称是本项目、但并非来自 `github.com/bakeryg/ArchivePasswordCracker`，
> 请当成未经审查的第三方代码。

### 发布流程（作者自用：给版本打签名标签）

用 SSH key 签名即可，**不需要装 GPG**。第一次配置一次：

```bat
git config --global user.name  "bakeryg"
git config --global user.email "你的邮箱"
git config --global gpg.format ssh
git config --global user.signingkey %USERPROFILE%\.ssh\id_ed25519.pub
```

再把公钥加到 GitHub：Settings → SSH and GPG keys → New SSH key → **Key type 选 Signing Key**。
以后每次发版：

```bat
git tag -s v1.0.0 -m "ArchivePasswordCracker v1.0.0"
git push origin v1.0.0
```

推上去后标签旁会出现 *Verified*。要强制所有提交都签名，可以在仓库 Settings → Branches
里给主分支打开 **Require signed commits**。

## 致谢

- 界面（`ui_mainwindow.py` / `ui_aboutdialog.py`）由原项目
  [GoogleLLP/Archive-password-cracker](https://github.com/GoogleLLP/Archive-password-cracker)
  的 Qt Designer `.ui` 文件转换而来
- 破解引擎：[Bandizip](https://www.bandisoft.com/bandizip/) 命令行工具
