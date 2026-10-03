#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# ArchivePasswordCracker —— 基于 Bandizip 引擎的压缩包密码破解工具（命令行版）
# Copyright (c) 2026 bakeryg
# SPDX-License-Identifier: MIT
# 项目地址: https://github.com/bakeryg/ArchivePasswordCracker
# ---------------------------------------------------------------------------
"""
bz_crack.py —— 用 Bandizip 的命令行工具 bz.exe 做字典爆破

为什么用它：
  * 直接借用 Bandizip 的解压引擎，支持 zip / zipx / 7z / rar / iso / tar / gz ...
  * 错误密码会“快速失败”（约 10~20ms），命中即停
  * 完全独立，不需要改动任何压缩包

字典格式：
  * 纯文本，一行一个密码；行首行尾空白会自动去掉
  * 编码自动识别：UTF-8 / UTF-8-BOM / GBK

用法示例：
  python bz_crack.py -a "D:\\test.zip" -d "dict.txt" -t 8
  python bz_crack.py -a "D:\\test.rar" -d "dict.txt" -t 8 --extract "D:\\out"
  python bz_crack.py -a "D:\\test.zip" -d "dict.txt" --no-password-check
"""

import argparse
import os
import queue
import subprocess
import sys
import threading
import time

BZ_CANDIDATES = [
    r"C:\Program Files\Bandizip\bz.exe",
    r"C:\Program Files (x86)\Bandizip\bz.exe",
]
CREATE_NO_WINDOW = 0x08000000

def _setup_console():
    """输出被重定向（管道/文件）时强制 UTF-8。
    否则 Windows 下会按控制台代码页(cp936)写，调用方若按 UTF-8 读就是乱码。"""
    for stream in (sys.stdout, sys.stderr):
        try:
            if not stream.isatty():
                stream.reconfigure(encoding="utf-8", errors="replace")
            else:
                stream.reconfigure(errors="replace")
        except Exception:
            pass


_setup_console()


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
    依次看：脚本同目录、同目录下的 cracker312 子目录、上一级目录。"""
    here = os.path.dirname(os.path.abspath(__file__))
    for d in (here, os.path.join(here, "cracker312"), os.path.dirname(here)):
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


def find_bz(explicit=None):
    if explicit:
        if os.path.isfile(explicit):
            return explicit
        sys.exit("[错误] 找不到 bz.exe: %s" % explicit)
    hint = read_bz_hint()
    if hint:
        return hint
    for c in BZ_CANDIDATES:
        if os.path.isfile(c):
            return c
    import shutil
    for name in ("bz.exe", "bz"):
        w = shutil.which(name)
        if w:
            return w
    sys.exit("[错误] 找不到 bz.exe。\n"
             "       请安装 Bandizip（默认目录），或双击运行「检测Bandizip.bat」，\n"
             "       或用 -j 参数指定 bz.exe 的完整路径。")


def read_dict(path, encoding=None):
    encs = [encoding] if encoding else ["utf-8-sig", "utf-8", "gbk", "latin-1"]
    for enc in encs:
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read().splitlines(), enc
        except (UnicodeDecodeError, LookupError):
            continue
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read().splitlines(), "utf-8(replace)"


def run_bz(bz, args, timeout):
    """执行 bz.exe，返回 (returncode, output, elapsed_ms)"""
    t0 = time.time()
    try:
        p = subprocess.run([bz] + args, stdin=subprocess.DEVNULL,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           timeout=timeout, creationflags=CREATE_NO_WINDOW)
        out = p.stdout.decode("utf-8", "replace")
        return p.returncode, out, (time.time() - t0) * 1000.0
    except subprocess.TimeoutExpired:
        return -1, "TIMEOUT", (time.time() - t0) * 1000.0
    except OSError as e:
        return -2, "OSError: %s" % e, (time.time() - t0) * 1000.0


def fmt_hms(sec):
    sec = int(sec)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    if h:
        return "%dh%02dm%02ds" % (h, m, s)
    if m:
        return "%dm%02ds" % (m, s)
    return "%ds" % s


class Cracker(object):
    def __init__(self, bz, archive, passwords, threads, timeout, verbose):
        self.bz = bz
        self.archive = archive
        self.passwords = passwords
        self.threads = threads
        self.timeout = timeout
        self.verbose = verbose
        self.q = queue.Queue(maxsize=threads * 8)
        self.stop = threading.Event()
        self.lock = threading.Lock()
        self.found = None
        self.done = 0
        self.total = len(passwords)
        self.errors = 0
        self.t0 = time.time()
        self.last_report = 0.0

    def _report(self, force=False):
        now = time.time()
        if not force and now - self.last_report < 0.5:
            return
        self.last_report = now
        with self.lock:
            done = self.done
        el = now - self.t0
        rate = done / el if el > 0 else 0
        line = "\r  进度 %d/%d (%.1f%%)  %.0f 个/秒  已用 %s" % (
            done, self.total, (done * 100.0 / self.total if self.total else 0),
            rate, fmt_hms(el))
        if self.total and rate > 0:
            left = (self.total - done) / rate
            line += "  预计剩余 %s" % fmt_hms(left)
        sys.stdout.write(line + "     ")
        sys.stdout.flush()

    def _producer(self):
        for pwd in self.passwords:
            if self.stop.is_set():
                break
            self.q.put(pwd)
        # 毒丸
        for _ in range(self.threads):
            self.q.put(None)

    def _worker(self, idx):
        while not self.stop.is_set():
            try:
                pwd = self.q.get(timeout=0.5)
            except queue.Empty:
                continue
            if pwd is None:
                return
            if self.stop.is_set():
                return
            rc, out, ms = run_bz(self.bz, ["t", "-p:" + pwd, "-y", self.archive], self.timeout)
            with self.lock:
                self.done += 1
            if rc == 0:
                with self.lock:
                    if self.found is None:
                        self.found = pwd
                self.stop.set()
                return
            if rc in (-1, -2):
                with self.lock:
                    self.errors += 1
                if self.errors <= 5:
                    sys.stdout.write("\n  [警告] 调用 bz.exe 异常 rc=%s: %s\n" % (rc, out.strip()[:200]))
                    sys.stdout.flush()
            if self.verbose:
                sys.stdout.write("\n  试过: %r -> rc=%s (%.0fms)\n" % (pwd, rc, ms))
                sys.stdout.flush()
            self._report()

    def run(self):
        pt = threading.Thread(target=self._producer, daemon=True)
        pt.start()
        ws = [threading.Thread(target=self._worker, args=(i,), daemon=True)
              for i in range(self.threads)]
        for w in ws:
            w.start()
        for w in ws:
            w.join()
        self.stop.set()
        self._report(force=True)
        sys.stdout.write("\n")
        return self.found


def main():
    ap = argparse.ArgumentParser(
        description="用 Bandizip (bz.exe) 做字典爆破",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-a", "--archive", required=True, help="要破解的压缩包路径")
    ap.add_argument("-d", "--dict", required=True, help="字典文件（一行一个密码）")
    ap.add_argument("-t", "--threads", type=int, default=min(8, (os.cpu_count() or 4)),
                    help="并发线程数，默认 8")
    ap.add_argument("-j", "--bz", default=None, help="bz.exe 路径（默认自动查找）")
    ap.add_argument("--timeout", type=float, default=120.0, help="单个密码的超时秒数，默认 120")
    ap.add_argument("--dict-encoding", default=None, help="强制指定字典编码，如 utf-8 / gbk")
    ap.add_argument("--extract", default=None, metavar="DIR",
                    help="找到密码后自动解压到该目录")
    ap.add_argument("--skip", type=int, default=0, help="跳过字典前 N 行（断点续跑）")
    ap.add_argument("--limit", type=int, default=0, help="最多尝试 N 条（0=全部）")
    ap.add_argument("--no-password-check", action="store_true",
                    help="跳过“压缩包是否加密”的预检查")
    ap.add_argument("--pw-out", default=None, metavar="DIR",
                    help="把密码记录写到该目录，而不是压缩包旁边")
    ap.add_argument("--no-pw-file", action="store_true",
                    help="命中后不写任何密码文件，只在屏幕显示")
    ap.add_argument("-v", "--verbose", action="store_true", help="打印每一次尝试")
    args = ap.parse_args()

    bz = find_bz(args.bz)
    archive = os.path.abspath(args.archive)
    if not os.path.isfile(archive):
        sys.exit("[错误] 压缩包不存在: %s" % archive)

    print("=" * 62)
    print(" bz_crack.py —— Bandizip 引擎字典爆破")
    print("=" * 62)
    print(" bz.exe   : %s" % bz)
    print(" 压缩包   : %s" % archive)
    print(" 并发线程 : %d" % args.threads)

    # 预检查：压缩包到底加没加密
    if not args.no_password_check:
        rc, out, ms = run_bz(bz, ["t", "-y", archive], args.timeout)
        if rc == 0:
            print("\n[提示] 这个压缩包**没有密码**（不加密就能通过完整性测试），无需破解。")
            print("       如仍要尝试，请加 --no-password-check")
            return
        if rc == 15:
            print(" 预检查   : 确认已加密（Password is needed）")
        else:
            print(" 预检查   : 未加密判定失败 rc=%s，继续尝试…" % rc)

    lines, enc = read_dict(args.dict, args.dict_encoding)
    pwds = [ln.strip() for ln in lines]
    pwds = [p for p in pwds if p]           # 去掉空行
    if args.skip:
        pwds = pwds[args.skip:]
    if args.limit:
        pwds = pwds[:args.limit]
    if not pwds:
        sys.exit("[错误] 字典里没有有效密码（文件是否为空？）")
    print(" 字典     : %s  (编码 %s, 有效密码 %d 条%s)" % (
        args.dict, enc, len(pwds), (", 跳过前 %d 条" % args.skip) if args.skip else ""))
    print("-" * 62)

    c = Cracker(bz, archive, pwds, args.threads, args.timeout, args.verbose)
    try:
        found = c.run()
    except KeyboardInterrupt:
        print("\n[中断] 用户取消")
        return

    if found is None:
        print("[结果] 字典跑完，没找到密码。（试过 %d 条，异常 %d 次）" % (c.done, c.errors))
        return

    print("[结果] ✅ 找到密码： %s" % found)

    # 密码记录文件的落点：
    #   默认 = 压缩包旁边（<压缩包>.password.txt）
    #   --pw-out DIR = 写到指定目录，不碰压缩包所在目录
    #   --no-pw-file = 完全不写文件
    written = None
    if args.no_pw_file:
        cands = []
    elif args.pw_out:
        cands = [os.path.join(os.path.abspath(args.pw_out),
                              os.path.basename(archive) + ".password.txt")]
    else:
        cands = [archive + ".password.txt",
                 os.path.join(os.path.dirname(os.path.abspath(__file__)), "found_password.txt"),
                 os.path.join(os.getcwd(), "found_password.txt")]
    for cand in cands:
        try:
            d = os.path.dirname(cand)
            if d:
                os.makedirs(d, exist_ok=True)
            with open(cand, "w", encoding="utf-8") as f:
                f.write(found + "\n")
            written = cand
            break
        except OSError:
            continue
    if written:
        print("       已写入: %s" % written)
    elif cands:
        print("       (无法写入密码文件，以上方输出为准)")

    if args.extract:
        outdir = os.path.abspath(args.extract)
        print("[解压] 正在解压到 %s ..." % outdir)
        rc, out, ms = run_bz(bz, ["x", "-p:" + found, "-y", "-o:" + outdir, archive], max(args.timeout, 600))
        if rc == 0:
            print("[解压] ✅ 完成")
        else:
            print("[解压] ❌ 失败 rc=%s\n%s" % (rc, out.strip()[:400]))


if __name__ == "__main__":
    main()
