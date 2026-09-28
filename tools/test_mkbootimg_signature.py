#!/usr/bin/env python3
import pathlib, struct, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
MK = ROOT / "ImageResources/mkbootimg.py"

def sig_size(path):
    data = path.read_bytes()[:4096]
    assert data[:8] == b"ANDROID!"
    assert struct.unpack_from("<I", data, 40)[0] == 4
    return struct.unpack_from("<I", data, 1580)[0]

with tempfile.TemporaryDirectory() as td:
    d = pathlib.Path(td)
    kernel = d / "kernel.bin"
    kernel.write_bytes(b"A" * 33)

    default = d / "default.img"
    subprocess.check_call([sys.executable, str(MK), "--kernel", str(kernel),
                           "-o", str(default), "--header_version", "4"])
    assert sig_size(default) == 4096
    assert default.stat().st_size == 4096 + 4096 + 4096

    cp2a = d / "cp2a.img"
    subprocess.check_call([sys.executable, str(MK), "--kernel", str(kernel),
                           "-o", str(cp2a), "--header_version", "4",
                           "--boot_signature_size", "0"])
    assert sig_size(cp2a) == 0
    assert cp2a.stat().st_size == 4096 + 4096

print("PASS: mkbootimg preserves default 4096 signature placeholder and supports CP2A-style size 0")
