#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Archive Password Toolkit —— 基于 Bandizip 引擎的压缩包密码破解工具
# Copyright (c) 2026 bakeryg
# SPDX-License-Identifier: MIT
# 项目地址: https://github.com/bakeryg/archive-password-toolkit
# ---------------------------------------------------------------------------
"""
cracker312.py —— Archive Password Toolkit 的 Python 3.12 + PySide6 版本

特点
  * 界面文件由 Qt Designer 的 .ui 只读转换而来（来源说明见 README / LICENSE）
  * 两个标签页：使用自定义字典（主内容） / 枚举破解
  * 破解引擎：Bandizip 命令行 bz.exe（zip / rar / 7z / zipx 等）

自定义字典 + 拖入：把压缩包拖进「使用自定义字典」的框里即开始破解，自动使用当前选中的字典。
"""

import collections
import itertools
import json
import os
import queue
import string
import subprocess
import sys
import threading
import time

from PySide6.QtCore import Qt, QPoint, QThread, QTimer, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (QApplication, QDialog, QFileDialog, QHBoxLayout,
                               QInputDialog, QLabel, QLineEdit, QMainWindow, QMenu,
                               QMessageBox, QPushButton, QVBoxLayout, QWidget)

from ui_mainwindow import Ui_MainWindow
from ui_aboutdialog import Ui_Dialog
import zipprobe

# ----------------------------------------------------------------------
# 常量
# ----------------------------------------------------------------------
SEED_DIGITS = "0123456789"
SEED_LOWER = string.ascii_lowercase
SEED_UPPER = string.ascii_uppercase
SEED_SYMBOLS = string.punctuation

FILE_FILTER_TXT = "文本文件 (*.txt);;全部文件 (*)"
FILE_FILTER_ZIP = ("压缩文件 (*.zip *.rar *.7z *.iso *.tar *.gz *.zipx *.001 *.bz2 *.xz);;"
                   "全部文件 (*)")
ARCHIVE_EXTS = (".zip", ".rar", ".7z", ".iso", ".tar", ".gz", ".zipx",
                ".001", ".bz2", ".xz")

BZ_CANDIDATES = [
    r"C:\Program Files\Bandizip\bz.exe",
    r"C:\Program Files (x86)\Bandizip\bz.exe",
]

MSG_TITLE = "提示"
MSG_WARNING = "警告"

START_CRACK = "开始破解"
STOP_CRACK = "停止破解"
START_EXPORT = "开始导出"
STOP_EXPORT = "停止导出"

CREATE_NO_WINDOW = 0x08000000
APP_NAME = "Archive Password Toolkit"
# 上传到自己的仓库后，把下面这行改成你的项目地址
APP_URL = "https://github.com/bakeryg/archive-password-toolkit"

HERE = os.path.dirname(os.path.abspath(__file__))


# ----------------------------------------------------------------------
# 工具函数
# ----------------------------------------------------------------------
def _decode_hint(raw):
    """bz_path.txt 的编码取决于写入时的控制台代码页（可能是 UTF-8 或 GBK），
    所以逐个编码试，并用 os.path.isfile 校验 —— 编码解错时路径必然不存在。"""
    for enc in ("utf-8-sig", "gbk", "mbcs", "latin-1"):
        try:
            v = raw.decode(enc).strip().strip('"').strip()
        except (UnicodeDecodeError, LookupError):
            continue
        if v and os.path.isfile(v):
            return v
    return None


def read_bz_hint():
    """读取「检测Bandizip.bat / DetectBandizip.bat」写下的 bz_path.txt。
    工作目录、程序目录、程序目录下的 cracker312 子目录、上一级目录都找一遍。"""
    dirs = [WORK_DIR, HERE, os.path.join(HERE, "cracker312"), os.path.dirname(HERE)]
    seen = set()
    for d in dirs:
        if not d or d in seen:
            continue
        seen.add(d)
        p = os.path.join(d, "bz_path.txt")
        try:
            with open(p, "rb") as f:
                raw = f.read()
        except OSError:
            continue
        v = _decode_hint(raw)
        if v:
            return v
    return None


def find_bz():
    # 1) 先看用户/检测脚本指定的路径
    hint = read_bz_hint()
    if hint:
        return hint
    # 2) 常见安装目录
    for c in BZ_CANDIDATES:
        if os.path.isfile(c):
            return c
    # 3) PATH
    import shutil
    for name in ("bz.exe", "bz"):
        w = shutil.which(name)
        if w:
            return w
    return None


def find_code_txt():
    """code.txt 优先找本目录，其次找上一级目录。"""
    for d in (HERE, os.path.dirname(HERE)):
        p = os.path.join(d, "code.txt")
        if os.path.isfile(p):
            return p
    return os.path.join(HERE, "code.txt")


# ---- 工作目录：缓存 / 历史 / 临时文件都放这儿，用户可自定义到别的盘 ----
CONFIG_FILE = os.path.join(HERE, "config.json")     # 引导配置，固定放程序目录
DEFAULT_WORK_DIR = HERE                             # 默认 = 程序目录（绿色可搬）


def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def save_config(d):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        return True
    except Exception:
        return False


def _usable_dir(path):
    if not path:
        return False
    try:
        os.makedirs(path, exist_ok=True)
        probe = os.path.join(path, ".write_test.tmp")
        with open(probe, "w") as f:
            f.write("x")
        os.remove(probe)
        return True
    except OSError:
        return False


def resolve_work_dir():
    wd = (load_config().get("work_dir") or "").strip()
    if wd and _usable_dir(wd):
        return os.path.abspath(wd)
    return DEFAULT_WORK_DIR


WORK_DIR = resolve_work_dir()

# ---- 字典历史（存在工作目录下的 dict_history.json）----
HISTORY_FILE = os.path.join(WORK_DIR, "dict_history.json")
MAX_HISTORY = 15


def set_temp_dir(path):
    """把本进程（及其子进程，如 bz.exe / 多进程工作进程）的临时目录指到工作目录，
    这样临时文件不会落到系统盘。"""
    for var in ("TMP", "TEMP"):
        try:
            os.environ[var] = path
        except Exception:
            pass


def load_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            out = []
            for p in data:
                if isinstance(p, str) and p and p not in out:
                    out.append(p)
            return out[:MAX_HISTORY]
    except Exception:
        pass
    return []


def save_history(lst):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(list(lst)[:MAX_HISTORY], f, ensure_ascii=False, indent=1)
        return True
    except Exception:
        return False


def _flags():
    return CREATE_NO_WINDOW if os.name == "nt" else 0


def bz_test(bz, archive, pwd, timeout=180):
    """返回 True 表示密码正确（bz.exe 退出码 0）。"""
    try:
        r = subprocess.run([bz, "t", "-p:" + pwd, "-y", archive],
                           stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, timeout=timeout,
                           creationflags=_flags())
        return r.returncode == 0
    except Exception:
        return False


def bz_encrypted_probe(bz, archive):
    """用一个随机生成的、不可能正确的密码再测一次，用来识别「根本没加密」的压缩包。

    bz.exe 对**未加密**的压缩包会给任何密码都返回 0（All OK），所以：
      * 这个瞎编的密码也能通过 → 包没有加密，之前那个"命中"是假象；
      * 返回非 0              → 包确实加密了，命中的密码才算数。
    """
    return bz_test(bz, archive, "apc-probe-" + os.urandom(16).hex())


def bz_extract(bz, archive, pwd, outdir, timeout=3600):
    try:
        r = subprocess.run([bz, "x", "-p:" + pwd, "-y", "-o:" + outdir, archive],
                           stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, timeout=timeout,
                           creationflags=_flags())
        return r.returncode == 0
    except Exception:
        return False


def detect_dict_encoding(path, probe_size=262144):
    """探测字典编码：只读文件头部试解，不把整本读进内存。"""
    try:
        with open(path, "rb") as f:
            head = f.read(probe_size)
    except OSError:
        return "utf-8"
    for enc in ("utf-8-sig", "utf-8", "gbk", "latin-1"):
        try:
            head.decode(enc)
            return enc
        except (UnicodeDecodeError, LookupError):
            continue
    return "utf-8"


def count_dict_lines(path):
    """二进制数行，只用于进度显示，O(1) 内存。"""
    n = 0
    try:
        with open(path, "rb") as f:
            while True:
                b = f.read(1 << 20)
                if not b:
                    break
                n += b.count(b"\n")
    except OSError:
        return 0
    return n


def iter_passwords(path, encoding=None, skip_comments=True):
    """流式逐行产出密码 —— 内存 O(1)，不再把整本字典读进 list。

    之前是 read().splitlines() 整表读入：100 万条约占 71 MB
    （75 字节/条），1000 万条就要 0.7 GB。"""
    enc = encoding or detect_dict_encoding(path)
    with open(path, "r", encoding=enc, errors="replace") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            if skip_comments and s.startswith("#"):
                continue
            yield s


def seed_of(digits, lower, upper, symbols):
    s = ""
    if digits:
        s += SEED_DIGITS
    if lower:
        s += SEED_LOWER
    if upper:
        s += SEED_UPPER
    if symbols:
        s += SEED_SYMBOLS
    return s


def gen_passwords(seed, mn, mx, fixed=None):
    """按位数从小到大枚举所有组合。

    fixed: {位置(从 1 开始): 字符} —— 这些位置写死，只有其余位置才用 seed 枚举。
           例：{1: "a", 3: "7"} 表示第 1 位是 a、第 3 位是 7。
           值写多个字符时从该位置起连续写死：{1: "abc"} 等于 1=a,2=b,3=c（也就是前缀 abc）。
    """
    fixed = fixed or {}
    for n in range(mn, mx + 1):
        pre = {}                        # 当前长度下，各位置的固定字符
        for pos, val in fixed.items():
            for k, ch in enumerate(val):
                p = pos + k
                if p <= n:
                    pre[p] = ch
        free = [i for i in range(1, n + 1) if i not in pre]
        for tup in itertools.product(seed, repeat=len(free)):
            out = [""] * n
            for p, ch in pre.items():
                out[p - 1] = ch
            for p, ch in zip(free, tup):
                out[p - 1] = ch
            yield "".join(out)


def total_of(seed, mn, mx, fixed=None):
    """组合总数（有固定位时只数真正要枚举的那些位置）。"""
    fixed = fixed or {}
    total = 0
    for n in range(mn, mx + 1):
        used = 0
        for pos, val in fixed.items():
            for k in range(len(val)):
                if pos + k <= n:
                    used += 1
        total += len(seed) ** (n - used)
    return total


def parse_fixed_positions(text):
    """把「1=a,3=7」解析成 {1: "a", 3: "7"}（位置从 1 开始数）。

    * 多组用逗号 / 分号 / 空格分开（中文逗号、中文分号也行）；
    * 值可以写多个字符，表示从该位置起连续写死：1=abc 等于 1=a,2=b,3=c；
    * 格式不对时抛 ValueError，消息直接给用户看。
    """
    raw = (text or "").replace("，", ",").replace("；", ";")
    parts = [c for c in raw.replace(";", " ").replace(",", " ").split() if c]
    out = {}
    for part in parts:
        if "=" not in part:
            raise ValueError("「%s」写法不对，应该是 位置=字符，例如 1=a,3=7" % part)
        k, v = part.split("=", 1)
        k = k.strip()
        if not k.isdigit() or int(k) < 1:
            raise ValueError("「%s」里的位置要是从 1 开始的数字" % part)
        if v == "":
            raise ValueError("「%s」没有写固定的字符" % part)
        out[int(k)] = v
    return out


# ----------------------------------------------------------------------
# 拖入控件
# ----------------------------------------------------------------------
class DropArea(QLabel):
    dropped = Signal(str)

    STYLE_IDLE = ("QLabel { border: 2px dashed #6aa9e0; border-radius: 10px;"
                  " background: #eef6ff; color: #2b5f8a; font-size: 13pt; }")
    STYLE_HOT = ("QLabel { border: 2px dashed #2e8b57; border-radius: 10px;"
                 " background: #e4f6e4; color: #1d6b3a; font-size: 13pt; }")

    def __init__(self, parent=None):
        QLabel.__init__(self, parent)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(96)
        self.setWordWrap(True)
        self.setStyleSheet(self.STYLE_IDLE)
        self.setText("把压缩包拖到这里\n(也可以点击本区域选择文件)")

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
            self.setStyleSheet(self.STYLE_HOT)
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dragLeaveEvent(self, e):
        self.setStyleSheet(self.STYLE_IDLE)

    def dropEvent(self, e):
        self.setStyleSheet(self.STYLE_IDLE)
        urls = e.mimeData().urls()
        if not urls:
            return
        e.acceptProposedAction()
        self.dropped.emit(urls[0].toLocalFile())

    def mouseReleaseEvent(self, e):
        QLabel.mouseReleaseEvent(self, e)
        path, _ = QFileDialog.getOpenFileName(self, "选择要破解的压缩包", "",
                                              FILE_FILTER_ZIP)
        if path:
            self.dropped.emit(path)


# ----------------------------------------------------------------------
# 破解线程
# ----------------------------------------------------------------------
class CrackWorker(QThread):
    progress = Signal(int)
    found = Signal(str)
    notfound = Signal(int)      # 参数＝已经试过的候选数
    error = Signal(str)
    info = Signal(str)

    FAST_CHUNK = 2000        # 每个子任务处理的候选数（控制内存与调度粒度）

    def __init__(self, bz, archive, pw_source, total, threads, parent=None):
        QThread.__init__(self, parent)
        self.bz = bz
        self.archive = archive
        self.pw_source = pw_source      # 可迭代对象（生成器或列表）
        self.total = total
        self.threads = max(1, int(threads))
        self._stop = threading.Event()
        self._done = 0
        self._lock = threading.Lock()
        self._result = None
        self._unencrypted = False       # 命中后复验发现"这个包根本没加密"
        self._last_emit = 0.0

    def stop(self):
        self._stop.set()

    # ---------------- 公共 ----------------
    @staticmethod
    def _chunks(it, size):
        buf = []
        for x in it:
            buf.append(x)
            if len(buf) >= size:
                yield buf
                buf = []
        if buf:
            yield buf

    def _emit_progress(self, done, force=False):
        now = time.time()
        if not force and now - self._last_emit < 0.2:
            return
        self._last_emit = now
        if self.total:
            self.progress.emit(min(99, int(done * 100 / self.total)))

    def _finish(self):
        # 命中后复验：未加密的压缩包对任何密码都返回 0，
        # 拿一个随机瞎编的密码测一次就能识别出来 —— 不然界面会显示一个"随机密码"。
        if self._result is not None and bz_encrypted_probe(self.bz, self.archive):
            with self._lock:
                self._result = None
            self._unencrypted = True

        self.progress.emit(100)
        if self._unencrypted:
            self.error.emit("这个压缩包没有加密，不需要密码。")
        elif self._result is not None:
            self.found.emit(self._result)
        else:
            self.notfound.emit(self._done)

    # ---------------- 入口 ----------------
    def run(self):
        probe = zipprobe.make_probe(self.archive)
        if probe is not None:
            self.info.emit("快速预筛已启用（%s）：候选密码在进程内校验，"
                           "命中后仍由 bz.exe 最终确认" % probe.kind)
            try:
                self._run_fast(probe)
                self._finish()
                return
            except Exception as ex:
                self.info.emit("快速路径异常(%s)，回落到 bz.exe" % ex)
            finally:
                probe.close()
        self._run_bz()
        self._finish()

    # ---------------- 快速路径（进程内预筛 + bz.exe 确认）----------------
    def _run_fast(self, probe):
        import multiprocessing
        done = 0
        hit = None
        src = self._chunks(self.pw_source, self.FAST_CHUNK)

        pool = None
        try:
            ctx = multiprocessing.get_context("spawn")
            pool = ctx.Pool(processes=self.threads,
                            initializer=zipprobe.worker_init,
                            initargs=(self.archive,))
        except Exception as ex:
            self.info.emit("多进程不可用(%s)，改用单线程预筛" % ex)
            pool = None

        if pool is not None:
            inflight = max(2, self.threads * 2)
            pending = collections.deque()
            exhausted = False
            try:
                while True:
                    while not exhausted and len(pending) < inflight:
                        try:
                            pending.append(pool.apply_async(
                                zipprobe.worker_check, (next(src),)))
                        except StopIteration:
                            exhausted = True
                            break
                    if not pending:
                        break
                    cnt, pwd = pending.popleft().get()
                    done += cnt
                    if pwd and bz_test(self.bz, self.archive, pwd):
                        hit = pwd
                        break
                    self._emit_progress(done)
                    if self._stop.is_set():
                        break
            finally:
                pool.terminate()
                pool.join()
        else:
            zipprobe.worker_init(self.archive)
            for chunk in src:
                cnt, pwd = zipprobe.worker_check(chunk)
                done += cnt
                if pwd and bz_test(self.bz, self.archive, pwd):
                    hit = pwd
                    break
                self._emit_progress(done)
                if self._stop.is_set():
                    break

        with self._lock:
            self._done = done
            self._result = hit

    # ---------------- 回落路径（每候选一次 bz.exe）----------------
    def _run_bz(self):
        bz, archive = self.bz, self.archive
        q = queue.Queue(maxsize=self.threads * 16)

        def producer():
            try:
                for pw in self.pw_source:
                    if self._stop.is_set():
                        break
                    q.put(pw)
            except Exception as ex:
                self.error.emit("读取密码出错: %s" % ex)
            finally:
                for _ in range(self.threads):
                    q.put(None)

        def worker():
            while not self._stop.is_set():
                item = q.get()
                if item is None:
                    return
                if bz_test(bz, archive, item):
                    with self._lock:
                        if self._result is None:
                            self._result = item
                    self._stop.set()
                    return
                with self._lock:
                    self._done += 1

        pt = threading.Thread(target=producer, daemon=True)
        pt.start()
        ws = [threading.Thread(target=worker, daemon=True) for _ in range(self.threads)]
        for w in ws:
            w.start()
        while any(w.is_alive() for w in ws):
            with self._lock:
                d = self._done
            self._emit_progress(d)
            time.sleep(0.12)
            if self._stop.is_set() and self._result is None:
                break
        self._stop.set()


# ----------------------------------------------------------------------
# 导出字典线程
# ----------------------------------------------------------------------
class ExtractWorker(QThread):
    """手动解压（点「解压位置」那一行右边的「解压」按钮时跑）。

    破解成功后本来就会自动解压，这个线程是给两种情况用的：
      * 破解时没填解压位置，事后想解压；
      * 密码已经知道（直接填在「密码是」框里），想再解一次。

    bz.exe 解压期间无法中断，所以 stop() 只是占位，保证关闭窗口的流程不报错。
    """
    done = Signal(str)
    failed = Signal(str)

    def __init__(self, bz, archive, pwd, outdir, parent=None):
        QThread.__init__(self, parent)
        self.bz = bz
        self.archive = archive
        self.pwd = pwd
        self.outdir = outdir

    def stop(self):
        pass

    def run(self):
        try:
            if not os.path.isdir(self.outdir):
                os.makedirs(self.outdir, exist_ok=True)
        except OSError as e:
            self.failed.emit("解压目录无法创建：%s" % e)
            return
        if bz_extract(self.bz, self.archive, self.pwd, self.outdir):
            self.done.emit(self.outdir)
        else:
            self.failed.emit("解压失败：密码不对、压缩包损坏，或目录没有写权限。")


class ExportWorker(QThread):
    progress = Signal(int)
    finished_ok = Signal(str, int)
    error = Signal(str)

    def __init__(self, path, seed, mn, mx, total, fixed=None, parent=None):
        QThread.__init__(self, parent)
        self.path = path
        self.seed = seed
        self.fixed = fixed or {}
        self.mn = mn
        self.mx = mx
        self.total = total
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def run(self):
        n = 0
        try:
            with open(self.path, "w", encoding="utf-8", newline="\n") as f:
                for pw in gen_passwords(self.seed, self.mn, self.mx, self.fixed):
                    if self._stop.is_set():
                        break
                    f.write(pw + "\n")
                    n += 1
                    if n % 5000 == 0:
                        self.progress.emit(min(100, int(n * 100 / self.total)) if self.total else 0)
        except Exception as ex:
            self.error.emit("写入字典失败: %s" % ex)
            return
        self.progress.emit(100)
        self.finished_ok.emit(self.path, n)


# ----------------------------------------------------------------------
# 关于窗口
# ----------------------------------------------------------------------
class AboutDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle("关于 " + APP_NAME)
        # 覆盖原 .ui 里的文字（那里写的是原作者信息），改为本项目的定位
        self.label_2.setText(
            APP_NAME + "\n\n"
            "作者：bakeryg\n"
            "基于 Bandizip 引擎的压缩包密码破解工具\n"
            "主推：自定义字典 + 拖入压缩包\n\n"
            "界面源自开源项目 GoogleLLP/Archive-password-cracker\n"
            "原作者：宗祥瑞\n"
            "破解引擎：Bandizip 的 bz.exe")

    def on_to_url(self):
        QDesktopServices.openUrl(QUrl(APP_URL))


# ----------------------------------------------------------------------
# 主窗口
# ----------------------------------------------------------------------
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle(APP_NAME)
        self._build_menu()

        self.app_dir = os.path.dirname(HERE)
        self.code_txt = find_code_txt()
        self.bz = find_bz()
        self.crack_worker = None
        self.export_worker = None
        self.last_mode = "external"     # 这次跑的是字典还是枚举（给"没找到"的提示用）
        self.last_dict = None           # 这次用的字典路径
        self.extract_worker = None      # 手动解压线程
        self.about_dlg = None

        # 字典历史：优先沿用上次用的（若文件还在），否则用 code.txt
        self.dict_history = load_history()
        self.current_dict = None
        for p in self.dict_history:
            if os.path.isfile(p):
                self.current_dict = p
                break
        if not self.current_dict:
            self.current_dict = self.code_txt

        # 线程数 / 批量数
        cores = os.cpu_count() or 4
        self.cpu_slider.setMaximum(cores)
        self.cpu_slider.setValue(cores)
        self.core_num.display(cores)
        self.dial.setValue(20000)
        self.batch_size.display(20000)

        # 位数范围默认值
        self.digit_min.setValue(1)
        self.digit_max.setValue(4)

        # 记住原 .ui 里的两个标签页（枚举破解 / 使用自定义字典）
        self.page_internal = self.dict_source.widget(0)
        self.page_external = self.dict_source.widget(1)

        # 把「当前字典 + 选择/历史 + 拖入框」并进「使用自定义字典」页
        self._build_drop_area()
        self._build_fixed_row()
        self._build_extract_button()

        # 主内容是「自定义字典 + 拖入」，所以把它排到第一个并默认打开，
        # 「枚举破解」（现场枚举）降为第二页
        self.dict_source.tabBar().moveTab(0, 1)
        self.dict_source.setCurrentIndex(0)

        self.set_dict(self.current_dict, add_history=False)

        self.statusbar.showMessage("就绪  |  引擎: %s  |  字典: %s  |  工作目录: %s"
                                   % (self.bz or "未找到 bz.exe", self.current_dict, WORK_DIR))

        if not self.bz:
            QMessageBox.warning(self, MSG_WARNING,
                                "没找到 Bandizip 的 bz.exe，无法破解。\n\n"
                                "解决办法（任选一个）：\n"
                                "  1. 安装 Bandizip（免费版即可），安装在默认目录；\n"
                                "  2. 如果用的是便携版/绿色版，请双击运行本目录下的\n"
                                "     「检测Bandizip.bat」，它会自动找到并记录路径；\n"
                                "  3. 也可以手动新建 bz_path.txt，里面只写一行\n"
                                "     bz.exe 的完整路径。\n\n"
                                "设置好之后直接点「开始破解」即可，不用重启程序。")

    # ---------------- 字典选择 / 历史 ----------------
    def set_dict(self, path, add_history=True):
        """切换当前字典，并（可选）记入历史。"""
        if not path:
            return
        self.current_dict = path
        self.dict_path.setText(path)
        if hasattr(self, "dict_label"):
            self.dict_label.setText(path)
            self.dict_label.setToolTip(path)
        if add_history and os.path.isfile(path):
            self.dict_history = [path] + [p for p in self.dict_history if p != path]
            self.dict_history = self.dict_history[:MAX_HISTORY]
            save_history(self.dict_history)
        if hasattr(self, "statusbar"):
            self.statusbar.showMessage("当前字典: %s" % path)

    def pick_dict(self):
        start = os.path.dirname(self.current_dict) if self.current_dict else ""
        path, _ = QFileDialog.getOpenFileName(self, "选择字典文件", start, FILE_FILTER_TXT)
        if path:
            self.set_dict(path)

    def show_dict_history(self):
        menu = QMenu(self)
        act = menu.addAction("当前: " + os.path.basename(self.current_dict or "无"))
        act.setEnabled(False)
        menu.addSeparator()
        alive = [p for p in self.dict_history if os.path.isfile(p)]
        if not alive:
            a = menu.addAction("(暂无历史字典)")
            a.setEnabled(False)
        else:
            for p in alive:
                a = menu.addAction(os.path.basename(p) + "    " + p)
                a.setToolTip(p)
                a.triggered.connect(lambda checked=False, pp=p: self.set_dict(pp))
            menu.addSeparator()
            b = menu.addAction("清空历史")
            b.triggered.connect(self.clear_dict_history)
        menu.exec(self.btn_dict_history.mapToGlobal(
            QPoint(0, self.btn_dict_history.height())))

    def clear_dict_history(self):
        self.dict_history = []
        save_history(self.dict_history)
        self.statusbar.showMessage("已清空字典历史")

    # ---------------- 工作目录（可自定义到别的盘）----------------
    def _build_menu(self):
        m = self.menuBar().addMenu("设置(&S)")
        a = m.addAction("选择工作目录...")
        a.setStatusTip("缓存、字典历史、临时文件都放在这个目录里")
        a.triggered.connect(self.choose_work_dir)
        b = m.addAction("打开工作目录")
        b.triggered.connect(self.open_work_dir)
        c = m.addAction("恢复为程序目录")
        c.triggered.connect(self.reset_work_dir)

    def _apply_work_dir(self, path):
        global WORK_DIR, HISTORY_FILE
        if not path:
            return False
        if not _usable_dir(path):
            QMessageBox.warning(self, MSG_WARNING,
                                "这个目录不可写，不能作为工作目录：\n%s" % path)
            return False
        new_dir = os.path.abspath(path)
        if os.path.abspath(WORK_DIR) == new_dir:
            self.statusbar.showMessage("工作目录已经是: %s" % new_dir)
            return True

        # 把已有的字典历史带过去（新目录里没有的话）
        old_hist = os.path.join(WORK_DIR, "dict_history.json")
        new_hist = os.path.join(new_dir, "dict_history.json")
        if os.path.isfile(old_hist) and not os.path.isfile(new_hist):
            try:
                import shutil
                shutil.copy2(old_hist, new_hist)
            except OSError:
                pass

        WORK_DIR = new_dir
        HISTORY_FILE = new_hist
        cfg = load_config()
        cfg["work_dir"] = "" if WORK_DIR == DEFAULT_WORK_DIR else WORK_DIR
        save_config(cfg)
        set_temp_dir(WORK_DIR)          # 临时文件也跟着走
        self.dict_history = load_history()
        self.statusbar.showMessage("工作目录已切换为: %s" % WORK_DIR)
        return True

    def choose_work_dir(self):
        start = WORK_DIR if os.path.isdir(WORK_DIR) else DEFAULT_WORK_DIR
        path = QFileDialog.getExistingDirectory(
            self, "选择工作目录（缓存 / 字典历史 / 临时文件都放这里）", start)
        if path:
            self._apply_work_dir(path)

    def open_work_dir(self):
        try:
            os.startfile(WORK_DIR)
        except Exception as ex:
            self.statusbar.showMessage("打不开目录: %s" % ex)

    def reset_work_dir(self):
        self._apply_work_dir(DEFAULT_WORK_DIR)

    # ---------------- 拖入区（并入「使用自定义字典」页）----------------
    def _build_drop_area(self):
        """把「当前字典 + 选择/历史 按钮 + 拖入框」追加进原「使用自定义字典」页。"""
        page = self.page_external
        lay = page.layout()          # 原 .ui 里的 QGridLayout

        # 第 1 行：当前字典 + 选择 + 历史
        row = QWidget(page)
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.addWidget(QLabel("当前字典:", row))
        self.dict_label = QLabel("", row)
        self.dict_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        h.addWidget(self.dict_label, 1)
        self.btn_pick_dict = QPushButton("选择字典...", row)
        self.btn_pick_dict.clicked.connect(self.pick_dict)
        h.addWidget(self.btn_pick_dict)
        self.btn_dict_history = QPushButton("历史字典 ▾", row)
        self.btn_dict_history.clicked.connect(self.show_dict_history)
        h.addWidget(self.btn_dict_history)
        lay.addWidget(row, 1, 0, 1, 3)

        # 第 2 行：说明
        hint = QLabel("把压缩包拖到下面的框里就开始破解（用的就是上面这本字典）\n"
                      "把 .txt 拖进来 = 切换字典；点一下框 = 选择压缩包", page)
        hint.setAlignment(Qt.AlignCenter)
        lay.addWidget(hint, 2, 0, 1, 3)

        # 第 3 行：拖入框
        self.drop_area = DropArea(page)
        self.drop_area.dropped.connect(self.on_drop_file)
        lay.addWidget(self.drop_area, 3, 0, 1, 3)

    def _build_fixed_row(self):
        """在枚举页加一行「固定位」输入：把某几位写死，只枚举其余位。"""
        row = QHBoxLayout()
        lab = QLabel("固定位", self.page_internal)
        self.fixed_edit = QLineEdit(self.page_internal)
        self.fixed_edit.setPlaceholderText("例如 1=a,3=7（留空＝全部枚举）")
        tip = ("把某些位置写死，只枚举其它位。写法：位置=字符，多个用逗号分开，例如\n"
               "    1=a,3=7   第 1 位是 a、第 3 位是 7\n"
               "    1=abc     前缀是 abc（等于 1=a,2=b,3=c）\n"
               "留空＝不固定。位置从 1 开始数；固定位要求的最短长度不够时，\n"
               "会自动把「最低位数」提到那个长度。")
        lab.setToolTip(tip)
        self.fixed_edit.setToolTip(tip)
        row.addWidget(lab)
        row.addWidget(self.fixed_edit)
        lay = getattr(self, "verticalLayout_2", None)     # 枚举页的竖向布局
        if lay is not None:
            lay.insertLayout(2, row)                      # 放在「位数」和「导出字典」之间
        else:
            self.verticalLayout.addLayout(row)

    def get_internal_params(self):
        """枚举页的参数：(字符集, 最低位, 最高位, 固定位)。

        固定位写错、或要求的长度超过位数上限时，弹提示并返回 None。
        """
        try:
            fixed = parse_fixed_positions(
                self.fixed_edit.text() if hasattr(self, "fixed_edit") else "")
        except ValueError as e:
            QMessageBox.warning(self, MSG_WARNING, str(e))
            return None
        seed = self.get_seed()
        mn, mx = self.get_digit_range()
        need = max([pos + len(val) - 1 for pos, val in fixed.items()] or [0])
        if need > mx:
            QMessageBox.warning(self, MSG_WARNING,
                                "固定位要求密码至少有 %d 位，但「最高位数」只有 %d。\n"
                                "请把最高位数改大，或删掉超出范围的固定位。" % (need, mx))
            return None
        if need > mn:
            mn = need           # 比 need 还短的长度里放不下固定位，直接从 need 起枚举
        return seed, mn, mx, fixed

    def _build_extract_button(self):
        """在「解压位置」那一行加一个手动解压按钮。"""
        self.btn_extract = QPushButton("解压", self.groupBox)
        self.btn_extract.setToolTip("用「密码是」框里的密码，解压到上面的解压位置。\n"
                                    "密码框为空时会先弹窗问你要密码。")
        self.btn_extract.clicked.connect(self.on_extract_clicked)
        lay = getattr(self, "horizontalLayout_4", None)      # 「解压位置」那一行
        if lay is not None:
            lay.addWidget(self.btn_extract)
        else:
            self.verticalLayout.addWidget(self.btn_extract)

    def on_extract_clicked(self):
        if self.extract_worker is not None and self.extract_worker.isRunning():
            return
        archive = self.zipfile_path.text().strip()
        if not archive or not os.path.isfile(archive):
            QMessageBox.warning(self, MSG_WARNING, "请选择压缩文件路径")
            return
        if not self.bz:
            self.bz = find_bz()
        if not self.bz:
            QMessageBox.warning(self, MSG_WARNING,
                                "没找到 bz.exe，无法解压。\n\n"
                                "请安装 Bandizip（默认目录），或双击运行本目录下的\n"
                                "「检测Bandizip.bat」自动定位并记录路径。")
            return
        outdir = self.extract_path.text().strip()
        if not outdir:
            outdir = QFileDialog.getExistingDirectory(self, "选择解压位置",
                                                      os.path.dirname(archive))
            if not outdir:
                return
            self.extract_path.setText(outdir)
        if os.path.isfile(outdir):
            QMessageBox.warning(self, MSG_WARNING, "解压位置是个文件，请选一个目录。")
            return
        pwd = self.password.text()          # 破解成功后密码就填在这里
        if not pwd:
            pwd, ok = QInputDialog.getText(self, "输入密码",
                                           "压缩包密码：", QLineEdit.Password)
            if not ok or not pwd:
                return
        self.btn_extract.setEnabled(False)
        self.statusbar.showMessage("正在解压到 %s …" % outdir)
        self.extract_worker = ExtractWorker(self.bz, archive, pwd, outdir, self)
        self.extract_worker.done.connect(self.on_extract_done)
        self.extract_worker.failed.connect(self.on_extract_failed)
        self.extract_worker.start()

    def on_extract_done(self, outdir):
        self.btn_extract.setEnabled(True)
        self.extract_worker = None
        self.statusbar.showMessage("已解压到 %s" % outdir)

    def on_extract_failed(self, msg):
        self.btn_extract.setEnabled(True)
        self.extract_worker = None
        self.statusbar.showMessage(msg)
        QMessageBox.warning(self, MSG_WARNING, msg)

    def on_drop_file(self, path):
        if not path or not os.path.isfile(path):
            self.statusbar.showMessage("无效的文件: %s" % path)
            return
        # 拖入的如果是 txt，就当作“换字典”，不当作要破解的目标
        if path.lower().endswith(".txt"):
            self.set_dict(path)
            self.drop_area.setText("已切换字典：%s\n再把压缩包拖进来即可" % os.path.basename(path))
            return
        if not self.current_dict or not os.path.isfile(self.current_dict):
            self.set_dict(self.code_txt, add_history=False)
        self.zipfile_path.setText(path)
        self.dict_path.setText(self.current_dict)
        self.drop_area.setText("已载入：%s\n字典：%s\n开始破解…"
                              % (os.path.basename(path), os.path.basename(self.current_dict)))
        self.statusbar.showMessage("拖入文件: %s  |  字典: %s"
                                   % (os.path.basename(path), self.current_dict))
        self.start_crack("external")

    # ---------------- 复选框 / 位数 ----------------
    def get_seed_selection(self):
        return [self.checkBox_num.isChecked(),
                self.checkBox_lower_letter.isChecked(),
                self.checkBox_upper_letter.isChecked(),
                self.checkBox_symbols.isChecked()]

    def validate_bool(self):
        sel = self.get_seed_selection()
        if not any(sel):
            QMessageBox.warning(self, MSG_WARNING, "请至少勾选一项")
            self.checkBox_num.setChecked(True)
            return False
        return True

    def get_seed(self):
        d, l, u, s = self.get_seed_selection()
        return seed_of(d, l, u, s)

    def get_digit_range(self):
        mn = self.digit_min.value()
        mx = self.digit_max.value()
        if mx < mn:
            mx = mn
            self.digit_max.setValue(mx)
        return mn, mx

    # ---------------- 路径选择 ----------------
    def select_export_path(self):
        path, _ = QFileDialog.getSaveFileName(self, "保存字典", "", FILE_FILTER_TXT)
        if path:
            self.export_path.setText(path)

    def select_zipfile_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择压缩文件", "", FILE_FILTER_ZIP)
        if path:
            self.zipfile_path.setText(path)

    def select_extract_path(self):
        path = QFileDialog.getExistingDirectory(self, "选择解压位置")
        if path:
            self.extract_path.setText(path)

    def select_dict_path(self):
        start = os.path.dirname(self.current_dict) if self.current_dict else ""
        path, _ = QFileDialog.getOpenFileName(self, "选择自定义字典", start, FILE_FILTER_TXT)
        if path:
            self.set_dict(path)      # 同步当前字典 + 记入历史

    def on_about(self):
        if self.about_dlg is None:
            self.about_dlg = AboutDialog(self)
        self.about_dlg.show()

    # ---------------- 导出字典 ----------------
    def on_export_dict(self):
        if self.export_worker is not None and self.export_worker.isRunning():
            self.export_worker.stop()
            self.export_worker = None
            self.button_export.setText(START_EXPORT)
            self.statusbar.showMessage("已停止导出")
            return

        if not self.validate_bool():
            return
        path = self.export_path.text().strip()
        if not path:
            QMessageBox.warning(self, MSG_WARNING, "请选择字典导出路径")
            return

        params = self.get_internal_params()
        if params is None:
            return
        seed, mn, mx, fixed = params
        total = total_of(seed, mn, mx, fixed)

        self.progress_export.setValue(0)
        self.button_export.setText(STOP_EXPORT)
        self.statusbar.showMessage("正在导出字典… 共 %d 条组合" % total)

        self.export_worker = ExportWorker(path, seed, mn, mx, total, fixed, self)
        self.export_worker.progress.connect(self.progress_export.setValue)
        self.export_worker.finished_ok.connect(self.on_export_done)
        self.export_worker.error.connect(lambda m: QMessageBox.warning(self, MSG_WARNING, m))
        self.export_worker.finished.connect(self._export_finished)
        self.export_worker.start()

    def on_export_progress_changed(self, value):
        pass

    def on_export_done(self, path, n):
        self.statusbar.showMessage("导出完成: %s（%d 条）" % (path, n))

    def _export_finished(self):
        self.button_export.setText(START_EXPORT)
        self.export_worker = None

    # ---------------- 破解 ----------------
    def on_crack_password(self, *args):
        """按钮点击入口（clicked 会带一个 bool 参数，用 *args 吃掉）。"""
        if self.crack_worker is not None and self.crack_worker.isRunning():
            self.crack_worker.stop()
            self.crack_worker = None
            self.button_crack.setText(START_CRACK)
            self.statusbar.showMessage("已停止破解")
            return
        self.start_crack(self.current_mode())

    def current_mode(self):
        """按标签页对象判断模式，不依赖序号。
        现在只有两页：「使用自定义字典」（含拖入区，默认）/「枚举破解」。"""
        w = self.dict_source.currentWidget()
        if w is getattr(self, "page_internal", None):
            return "internal"
        return "external"

    def start_crack(self, mode):
        """mode: "internal"=枚举破解（字符集+位数现场枚举）   "external"=自定义字典（含拖入）"""
        if self.crack_worker is not None and self.crack_worker.isRunning():
            return
        archive = self.zipfile_path.text().strip()
        if not archive or not os.path.isfile(archive):
            QMessageBox.warning(self, MSG_WARNING, "请选择压缩文件路径")
            return
        if not self.bz:
            # 启动时没找到，现在再找一次：这样"先开着程序、后来才装 Bandizip"
            # 或者刚跑完「检测Bandizip.bat」的情况下，不用重启程序
            self.bz = find_bz()
        if not self.bz:
            QMessageBox.warning(self, MSG_WARNING,
                                "没找到 bz.exe，无法破解。\n\n"
                                "请安装 Bandizip（默认目录），或双击运行本目录下的\n"
                                "「检测Bandizip.bat」自动定位并记录路径。")
            return
        self.statusbar.showMessage("引擎: %s" % self.bz)

        # 未加密的 zip：加密标志位就在目录头里，瞬间就能判断，
        # 免得白试一遍、更不会把第一个候选密码当成答案显示出来。
        try:
            _pr = zipprobe.ZipProbe(archive)
            _plain_zip = (_pr.kind is None) and (_pr.encrypted is False)
            _pr.close()
        except Exception:
            _plain_zip = False
        if _plain_zip:
            QMessageBox.information(self, MSG_WARNING,
                                    "这个压缩包没有加密，不需要密码，可以直接解压。")
            return

        self.last_mode = mode

        if mode == "internal":
            if not self.validate_bool():
                return
            params = self.get_internal_params()
            if params is None:
                return
            seed, mn, mx, fixed = params
            total = total_of(seed, mn, mx, fixed)
            source = gen_passwords(seed, mn, mx, fixed)
            fix_desc = ("  固定位 " + ",".join("%d=%s" % (p, v)
                                               for p, v in sorted(fixed.items()))) if fixed else ""
            src_desc = "枚举: %s  位数 %d~%d%s  共 %d 种组合" % (seed, mn, mx, fix_desc, total)
        else:
            path = self.dict_path.text().strip()
            if not path:
                path = self.current_dict or self.code_txt
            if not path or not os.path.isfile(path):
                QMessageBox.warning(self, MSG_WARNING, "请选择字典路径")
                return
            # 记入历史（包含从「使用自定义字典」标签页手填路径的情况）
            if os.path.abspath(path) != os.path.abspath(self.current_dict or ""):
                self.set_dict(path)
            # 流式读取：不把整本字典读进内存
            total = count_dict_lines(path)
            if total <= 0:
                QMessageBox.warning(self, MSG_WARNING, "字典里没有有效密码")
                return
            self.last_dict = path
            source = iter_passwords(path)
            src_desc = "字典: %s  约 %d 行" % (path, total)

        self.progress_crack.setValue(0)
        self.password.setText("")
        self.button_crack.setText(STOP_CRACK)
        self.statusbar.showMessage("正在破解… %s" % src_desc)

        threads = self.cpu_slider.value()
        self.crack_worker = CrackWorker(self.bz, archive, source, total, threads, self)
        self.crack_worker.progress.connect(self.progress_crack.setValue)
        self.crack_worker.found.connect(self.on_crack_found)
        self.crack_worker.notfound.connect(self.on_crack_notfound)
        self.crack_worker.error.connect(lambda m: QMessageBox.warning(self, MSG_WARNING, m))
        self.crack_worker.info.connect(self.statusbar.showMessage)
        self.crack_worker.finished.connect(self._crack_finished)
        self.crack_worker.start()

    def on_crack_progress_changed(self, value):
        pass

    def on_crack_found(self, pwd):
        self.password.setText(pwd)
        self.progress_crack.setValue(100)
        self.statusbar.showMessage("破解成功，密码是: %s" % pwd)
        self.drop_area.setText("破解成功！密码: %s" % pwd)

        outdir = self.extract_path.text().strip()
        if outdir:
            if os.path.isdir(outdir):
                self.statusbar.showMessage("破解成功，密码是: %s  |  正在解压…" % pwd)
                ok = bz_extract(self.bz, self.zipfile_path.text().strip(), pwd, outdir)
                self.statusbar.showMessage(
                    ("破解成功，密码是: %s  |  已解压到 %s" % (pwd, outdir)) if ok
                    else ("破解成功，密码是: %s  |  解压失败" % pwd))

    def on_crack_notfound(self, done=0):
        self.progress_crack.setValue(100)
        self.password.setText("")
        tried = ("（已试 %d 条）" % int(done or 0)) if done else ""
        self.statusbar.showMessage("破解失败，没找到密码%s" % tried)
        if getattr(self, "last_mode", "external") == "internal":
            self.drop_area.setText("枚举范围跑完，没找到密码%s\n"
                                   "可扩大字符集或位数范围再试" % tried)
        else:
            name = os.path.basename(getattr(self, "last_dict", None) or self.current_dict or "")
            if name:
                self.drop_area.setText("没找到密码%s\n可把更多密码加进当前字典（%s）再试"
                                       % (tried, name))
            else:
                self.drop_area.setText("没找到密码%s\n可把更多密码加进当前字典再试" % tried)

    def _crack_finished(self):
        self.button_crack.setText(START_CRACK)
        self.crack_worker = None

    def closeEvent(self, e):
        for w in (self.crack_worker, self.export_worker, self.extract_worker):
            if w is not None and w.isRunning():
                w.stop()
                w.wait(2000)
        QMainWindow.closeEvent(self, e)


def main():
    args = sys.argv[1:]
    target = ""
    if "--open" in args:
        i = args.index("--open")
        if i + 1 < len(args):
            target = args[i + 1]
    elif args:
        # 把压缩包直接拖到 main.exe / 启动.bat 上时，参数就是压缩包路径
        target = args[0]

    # 临时文件指到工作目录，避免落到系统盘（子进程 bz.exe / 工作进程也会继承）
    set_temp_dir(WORK_DIR)

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    if target and os.path.isfile(target):
        # 等窗口显示出来再自动开跑
        QTimer.singleShot(500, lambda: win.on_drop_file(target))
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
