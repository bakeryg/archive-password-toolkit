# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Archive Password Toolkit —— 基于 Bandizip 引擎的压缩包密码破解工具
# Copyright (c) 2026 bakeryg
# SPDX-License-Identifier: MIT
# 项目地址: https://github.com/bakeryg/archive-password-toolkit
# ---------------------------------------------------------------------------
"""
zipprobe.py —— zip 密码的「进程内快速预筛」

为什么需要它：
    用 bz.exe 试密码，每个候选都要起一个进程（实测约 20 ms）；
    而 zip 的密码对错判断其实只要几微秒 —— 根本不需要解压。

原理（只用标准库，不引入依赖）：
  * ZipCrypto（传统 PKWARE 加密，Bandizip/WinRAR 的 zip 默认就是它）
    用密码解出条目的 12 字节加密头，比对第 12 字节的解密结果与「校验字节」
    （未置位 0x08 时取 CRC 高字节，否则取 DOS 时间高字节）。
    通过后再解密紧随其后的若干字节并尝试 inflate —— 对 deflate 条目能把
    误报率从 1/256 压到几乎为零。
  * WinZip AES（method=99）
    PBKDF2-HMAC-SHA1(密码, salt, 1000 轮) 派生密钥的最后 2 字节就是密码
    校验值，比对即可（误报率 1/65536）。

重要：这里只是「预筛」。凡是预筛通过的候选，仍然交给 bz.exe 做最终确认，
所以破解结果与原实现完全一致；预筛失败（不是 zip / 没加密 / 结构异常）时
调用方自动回落到 bz.exe 老路径。

自测：  python zipprobe.py
"""

import hashlib
import io
import os
import struct
import subprocess
import sys
import time
import zipfile
import zlib

CREATE_NO_WINDOW = 0x08000000
_CRC_TABLE = None


def _crc_table():
    global _CRC_TABLE
    if _CRC_TABLE is None:
        t = []
        for i in range(256):
            c = i
            for _ in range(8):
                c = (c >> 1) ^ (0xEDB88320 if (c & 1) else 0)
            t.append(c)
        _CRC_TABLE = t
    return _CRC_TABLE


class ZipProbe(object):
    """针对一个 zip 文件做密码预筛。"""

    def __init__(self, path):
        self.usable = False
        self.kind = None          # "zipcrypto" / "aes"
        self.encrypted = None     # True=有加密条目 / False=确认没加密 / None=判断不了
        self.reason = ""
        self._f = None
        self._entry = None
        self._header = b""
        self._check = 0
        self._salt = b""
        self._verifier = b""
        self._dklen = 0
        self._method = 0
        self._data_off = 0
        self._csize = 0
        self._open(path)

    # ------------------------------------------------------------------
    def _fail(self, why):
        self.reason = why
        self.usable = False
        return

    def _open(self, path):
        try:
            zf = zipfile.ZipFile(path, "r")
        except Exception as e:
            return self._fail("不是 zip: %s" % e)

        info = None
        try:
            for it in zf.infolist():
                if (it.flag_bits & 0x1) and not it.is_dir():
                    info = it
                    break
        except Exception as e:
            return self._fail("读取目录失败: %s" % e)
        finally:
            try:
                zf.close()
            except Exception:
                pass

        if info is None:
            self.encrypted = False      # 结构解析成功，但一个加密条目都没有
            return self._fail("没有加密条目")

        try:
            f = open(path, "rb")
        except OSError as e:
            return self._fail("打不开文件: %s" % e)

        try:
            f.seek(info.header_offset)
            lh = f.read(30)
            if len(lh) < 30:
                raise ValueError("local header 不足 30 字节")
            (sig, ver, flag, method, mtime, mdate, crc,
             csize, usize, nlen, elen) = struct.unpack("<IHHHHHIIIHH", lh)
            if sig != 0x04034B50:
                raise ValueError("local header 签名不符")
            f.seek(info.header_offset + 30 + nlen)
            extra = f.read(elen) if elen else b""
            self._data_off = info.header_offset + 30 + nlen + elen
            self._csize = csize or info.compress_size
        except Exception as e:
            try:
                f.close()
            except Exception:
                pass
            return self._fail("解析 local header 失败: %s" % e)

        self._f = f
        self._entry = info
        self._method = method

        # ---------------- WinZip AES ----------------
        if method == 99:
            strength = None
            i = 0
            while i + 4 <= len(extra):
                hid, hsz = struct.unpack("<HH", extra[i:i + 4])
                body = extra[i + 4:i + 4 + hsz]
                if hid == 0x9901 and len(body) >= 7:
                    strength = body[4]
                    break
                i += 4 + hsz
            if strength not in (1, 2, 3):
                return self._fail("AES 强度字段异常: %r" % strength)
            saltlen = {1: 8, 2: 16, 3: 32}[strength]
            self._dklen = {1: 32, 2: 48, 3: 64}[strength]
            try:
                f.seek(self._data_off)
                self._salt = f.read(saltlen)
                self._verifier = f.read(2)
            except OSError as e:
                return self._fail("读 AES salt 失败: %s" % e)
            if len(self._salt) != saltlen or len(self._verifier) != 2:
                return self._fail("AES salt/verifier 不完整")
            self.kind = "aes"
            self.usable = True
            self.encrypted = True
            return

        # ---------------- ZipCrypto ----------------
        try:
            f.seek(self._data_off)
            self._header = f.read(12)
        except OSError as e:
            return self._fail("读加密头失败: %s" % e)
        if len(self._header) != 12:
            return self._fail("加密头不足 12 字节")

        flag_bits = flag or info.flag_bits
        if flag_bits & 0x08:
            self._check = (mtime >> 8) & 0xFF
        else:
            self._check = ((crc or info.CRC) >> 24) & 0xFF
        self._method = method
        self.kind = "zipcrypto"
        self.usable = True
        self.encrypted = True

    # ------------------------------------------------------------------
    def _candidates_bytes(self, password):
        """密码 -> 待试的字节串。非 ASCII 时同时试 UTF-8 和 GBK，
        因为不同打包工具写进 zip 的密码字节编码不一样。"""
        try:
            b = password.encode("utf-8")
        except Exception:
            return ()
        if all(c < 128 for c in b):
            return (b,)
        out = [b]
        try:
            g = password.encode("gbk")
            if g != b:
                out.append(g)
        except Exception:
            pass
        return tuple(out)

    def check(self, password):
        """返回 True 表示「很可能是正确密码」（仍需 bz.exe 最终确认）。"""
        if not self.usable:
            return False
        for pw in self._candidates_bytes(password):
            if self.kind == "aes":
                if self._check_aes(pw):
                    return True
            else:
                if self._check_zipcrypto(pw):
                    return True
        return False

    # ------------------------------------------------------------------
    def _check_aes(self, pw):
        try:
            dk = hashlib.pbkdf2_hmac("sha1", pw, self._salt, 1000, self._dklen)
        except Exception:
            return False
        return dk[-2:] == self._verifier

    def _check_zipcrypto(self, pw):
        tab = _crc_table()
        k0, k1, k2 = 0x12345678, 0x23456789, 0x34567890
        for b in pw:
            k0 = ((k0 >> 8) ^ tab[(k0 ^ b) & 0xFF]) & 0xFFFFFFFF
            k1 = ((k1 + (k0 & 0xFF)) * 134775813 + 1) & 0xFFFFFFFF
            k2 = ((k2 >> 8) ^ tab[(k2 ^ (k1 >> 24)) & 0xFF]) & 0xFFFFFFFF

        hdr = self._header
        # 解开 12 字节加密头
        plain = bytearray(12)
        for i in range(12):
            t = (k2 | 2) & 0xFFFF
            c = hdr[i] ^ (((t * (t ^ 1)) >> 8) & 0xFF)
            plain[i] = c
            k0 = ((k0 >> 8) ^ tab[(k0 ^ c) & 0xFF]) & 0xFFFFFFFF
            k1 = ((k1 + (k0 & 0xFF)) * 134775813 + 1) & 0xFFFFFFFF
            k2 = ((k2 >> 8) ^ tab[(k2 ^ (k1 >> 24)) & 0xFF]) & 0xFFFFFFFF

        if plain[11] != self._check:
            return False

        # 12 字节头通过只代表 1/256，继续解密数据头并试着 inflate
        if self._method != 8:
            return True          # 非 deflate（如 stored）没法进一步确认
        return self._inflate_probe(k0, k1, k2, tab)

    def _inflate_probe(self, k0, k1, k2, tab):
        """解密紧随其后的若干字节并尝试 inflate；失败即可断定密码不对。"""
        n = 256
        if self._csize:
            n = min(n, max(0, self._csize - 12))
        if n <= 0:
            return True
        try:
            self._f.seek(self._data_off + 12)
            buf = self._f.read(n)
        except OSError:
            return True
        if not buf:
            return True

        out = bytearray(len(buf))
        for i, c in enumerate(buf):
            t = (k2 | 2) & 0xFFFF
            p = c ^ (((t * (t ^ 1)) >> 8) & 0xFF)
            out[i] = p
            k0 = ((k0 >> 8) ^ tab[(k0 ^ p) & 0xFF]) & 0xFFFFFFFF
            k1 = ((k1 + (k0 & 0xFF)) * 134775813 + 1) & 0xFFFFFFFF
            k2 = ((k2 >> 8) ^ tab[(k2 ^ (k1 >> 24)) & 0xFF]) & 0xFFFFFFFF

        d = zlib.decompressobj(-15)
        try:
            d.decompress(bytes(out))
        except zlib.error:
            return False
        return True

    def close(self):
        if self._f is not None:
            try:
                self._f.close()
            except Exception:
                pass
            self._f = None

    def __del__(self):
        self.close()


# ======================================================================
# 多进程快筛用的模块级函数（必须放在模块级才能被 pickle）
# ======================================================================
_PROBE = None


def worker_init(archive_path):
    """进程池初始化：每个工作进程各自持有一个 probe（文件句柄不跨进程）。"""
    global _PROBE
    try:
        p = ZipProbe(archive_path)
        _PROBE = p if p.usable else None
    except Exception:
        _PROBE = None


def worker_check(chunk):
    """检查一批候选密码，返回 (已检查条数, 命中的密码或 None)。

    一旦命中就提前返回，剩余候选不计入（父进程会终止整个池）。"""
    p = _PROBE
    if p is None:
        return (0, None)
    n = 0
    for pw in chunk:
        n += 1
        if p.check(pw):
            return (n, pw)
    return (n, None)


def make_probe(archive_path):
    """外面用来判断这个包能不能走快速路径；不能则返回 None。"""
    try:
        p = ZipProbe(archive_path)
    except Exception:
        return None
    if p.usable:
        return p
    p.close()
    return None


# ======================================================================
# 自测 / 基准：python zipprobe.py
# ======================================================================
def _self_test():
    bz = None
    for c in (r"C:\Program Files\Bandizip\bz.exe",
              r"C:\Program Files (x86)\Bandizip\bz.exe"):
        if os.path.isfile(c):
            bz = c
            break
    here = os.path.dirname(os.path.abspath(__file__))
    hint = os.path.join(here, "bz_path.txt")
    if bz is None and os.path.isfile(hint):
        for enc in ("utf-8-sig", "gbk", "mbcs", "latin-1"):
            try:
                v = io.open(hint, "rb").read().decode(enc).strip().strip('"')
            except Exception:
                continue
            if os.path.isfile(v):
                bz = v
                break
    tmp = os.path.join(os.environ.get("TEMP", "."), "zipprobe_test")
    os.makedirs(tmp, exist_ok=True)
    payload = os.path.join(tmp, "p.bin")
    io.open(payload, "wb").write(b"hello zipprobe" * 5000)

    cases = [("ascii", "SEKRET123", bz), ("cn", "密码测试123", bz)]
    print("bz.exe =", bz)
    ok = True
    for tag, pwd, _ in cases:
        if not bz:
            print("  跳过 %s（没有 bz.exe）" % tag)
            continue
        z = os.path.join(tmp, "t_%s.zip" % tag)
        if os.path.isfile(z):
            os.remove(z)
        subprocess.run([bz, "c", "-fmt:zip", "-p:" + pwd, "-y", z, payload],
                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW)
        if not os.path.isfile(z):
            print("  %s: 造包失败" % tag)
            ok = False
            continue
        pr = ZipProbe(z)
        if not pr.usable:
            print("  %s: 预筛不可用（%s）" % (tag, pr.reason))
            ok = False
            continue
        good = pr.check(pwd)
        bad = [pr.check("wrong%d" % i) for i in range(3000)]
        fp = sum(1 for x in bad if x)
        # 基准
        t0 = time.perf_counter()
        N = 20000
        for i in range(N):
            pr.check("pw%d" % i)
        us = (time.perf_counter() - t0) / N * 1e6
        print("  %-6s kind=%-9s 正确密码=%s  3000 个错误密码误报=%d (%.3f%%)  %.1f 微秒/次 (~%.0f 个/秒)"
              % (tag, pr.kind, good, fp, fp / 30.0, us, 1e6 / us))
        if not good or fp:
            ok = False
        pr.close()
    print("自测%s" % ("通过" if ok else "失败"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(_self_test())
