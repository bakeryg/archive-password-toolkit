# AUTHORS — 作者与第三方来源 / Authors & third-party credits

## 本项目 / This project

**Archive Password Toolkit**

| | |
|---|---|
| 作者 / Author | **bakeryg** |
| 项目地址 / Project | <https://github.com/bakeryg/archive-password-toolkit> |
| 许可 / License | MIT（见 [`LICENSE`](LICENSE) / see [`LICENSE`](LICENSE)） |

Copyright (c) 2026 bakeryg

本项目的原创部分包括：`cracker312.py`（图形界面与破解调度）、`zipprobe.py`（进程内
zip 密码快速预筛）、`bz_crack.py`（命令行版）、`launcher.c`（启动壳）、`make_icon.py`
与图标、各 `.bat` 脚本、以及本 README / AUTHORS 文档。

The original parts of this project are `cracker312.py` (GUI and cracking orchestration),
`zipprobe.py` (in-process ZIP password pre-filter), `bz_crack.py` (command-line version),
`launcher.c` (launcher), `make_icon.py` plus the icon, the `.bat` scripts, and the
README / AUTHORS documents.

---

## 第三方来源 / Third-party credits

### 界面文件 / Interface files

`ui_mainwindow.py` 和 `ui_aboutdialog.py` 由 Qt Designer 的 `.ui` 文件经 `pyside6-uic`
转换而来（本项目只做只读转换与少量文字替换）。原始 `.ui` 来自开源项目：

- [GoogleLLP/Archive-password-cracker](https://github.com/GoogleLLP/Archive-password-cracker)
- 原作者 / Original author: **宗祥瑞**

### 引擎 / engine

- [Bandizip](https://www.bandisoft.com/bandizip/) 的命令行工具 `bz.exe`
- Copyright (c) Bandisoft。本项目**只调用使用者本机已安装的** Bandizip，
  不包含、不修改、也不再分发它的任何代码或文件。

### 运行库 / Runtime

- [PySide6](https://www.qt.io/)（Qt for Python）—— 由使用者自行 `pip install`，
  本项目不打包、不修改它。

---

## 二次分发时请注意 / If you fork or redistribute

- MIT 的全部要求就是**保留版权声明与许可文本** —— 请勿删除本文件和 `LICENSE`。
- 界面文件的上游署名请一并保留，说明见 `LICENSE` 底部。
- 如果改动了本项目，请在 commit 里如实说明；不要把他人的成果改个名字当成自己的。
