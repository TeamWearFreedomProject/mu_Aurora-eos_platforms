#!/usr/bin/env python3
"""Offline structural validation; does not demonstrate hardware bootability."""
import argparse
import hashlib
import json
import pathlib
import struct
import sys

HEADER_PAGE = 4096
MAX_BOOT_IMAGE = 64 * 1024 * 1024
EXPECTED_FD_SIZE = 0x002BF000
INHERITED_RELOCATION = 0x5FC41000

def sha256_file(path, offset=0, count=None):
    h = hashlib.sha256()
    with path.open("rb") as f:
        f.seek(offset)
        remaining = count
        while True:
            amount = 1024 * 1024 if remaining is None else min(1024 * 1024, remaining)
            if amount <= 0:
                break
            data = f.read(amount)
            if not data:
                if remaining is not None:
                    raise ValueError("image shorter than boot header advertises")
                break
            h.update(data)
            if remaining is not None:
                remaining -= len(data)
    return h.hexdigest()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("bootstrap", "shim", "fd", "payload", "image", "manifest"):
        p.add_argument("--" + name, required=True, type=pathlib.Path)
    a = p.parse_args()

    assert a.bootstrap.is_file() and a.shim.is_file() and a.fd.is_file()
    parts = (a.bootstrap, a.shim, a.fd)
    assert all(x.stat().st_size > 0 for x in parts)
    assert a.fd.stat().st_size == EXPECTED_FD_SIZE, "FD does not match inherited FDF size"

    with a.shim.open("rb") as f:
        shim = f.read(64)
    assert len(shim) == 64 and shim[56:60] == b"ARM\x64", "BootShim ARM64 header missing"
    assert struct.unpack_from("<Q", shim, 8)[0] == INHERITED_RELOCATION
    assert struct.unpack_from("<Q", shim, 16)[0] == EXPECTED_FD_SIZE

    expected_kernel_size = sum(x.stat().st_size for x in parts)
    assert a.payload.stat().st_size == expected_kernel_size
    if HEADER_PAGE + ((expected_kernel_size + 4095) // 4096) * 4096 + 4096 > MAX_BOOT_IMAGE:
        raise ValueError("combined image exceeds 64 MiB preliminary size limit")

    with a.payload.open("rb") as payload:
        for part in parts:
            with part.open("rb") as source:
                while True:
                    block = source.read(1024 * 1024)
                    if not block:
                        break
                    if payload.read(len(block)) != block:
                        raise ValueError(f"payload differs from {part}")
        assert payload.read(1) == b"", "trailing payload bytes"

    with a.image.open("rb") as img:
        header = img.read(HEADER_PAGE)
        assert len(header) == HEADER_PAGE and header[:8] == b"ANDROID!"
        kernel_size, ramdisk_size = struct.unpack_from("<II", header, 8)
        header_size = struct.unpack_from("<I", header, 20)[0]
        header_version = struct.unpack_from("<I", header, 40)[0]
        assert header_version == 4 and header_size == 1584, "not boot header v4"
        assert ramdisk_size == 0, "unexpected ramdisk in experimental image"
        assert kernel_size == expected_kernel_size, "kernel size mismatch"

    # The in-tree mkbootimg.py appends a 4096-byte GKI boot signature
    # placeholder even when no signing key is provided. It contains zeros,
    # not an authenticated signature; this does NOT establish AVB trust.
    sig_size = struct.unpack_from("<I", header, 1580)[0]
    assert sig_size == 4096, "unexpected v4 signature-section size"
    expected_img_size = HEADER_PAGE + ((kernel_size + 4095) // 4096) * 4096 + sig_size
    assert a.image.stat().st_size == expected_img_size, "boot image size mismatch"
    with a.image.open("rb") as img:
        img.seek(expected_img_size - sig_size)
        assert img.read(sig_size) == bytes(sig_size), "unsigned placeholder differs"
    payload_sha = sha256_file(a.payload)
    image_kernel_sha = sha256_file(a.image, HEADER_PAGE, kernel_size)
    assert image_kernel_sha == payload_sha, "packaged payload SHA256 mismatch"

    summary = {
        "format": "Android boot image v4",
        "device_target": "Pixel Watch 2 (aurora) EXPERIMENTAL",
        "observed_target_build": "CP3A.260905.002.E1",
        "CP3A_FIRMWARE_COMPATIBILITY_VERIFIED": False,
        "HARDWARE_TESTED": False,
        "SAFE_TO_FLASH": False,
        "AVB_VERIFIED": False,
        "GKI_BOOT_SIGNATURE": "4096-byte ZERO placeholder (NOT SIGNED)",
        "BOOTSTRAP_PROVENANCE": "inherited WOA-Project Watch3 build asset, not verified for Watch2",
        "BOOTSHIM_MEMORY_RELOCATION_VERIFIED_FOR_WATCH2": False,
        "ACPI_AND_FDF_VERIFIED_FOR_WATCH2": False,
        "inherited_bootshim_relocation_hex": hex(INHERITED_RELOCATION),
        "fd_size_bytes": EXPECTED_FD_SIZE,
        "kernel_payload_size_bytes": kernel_size,
        "boot_image_size_bytes": a.image.stat().st_size,
        "boot_image_sha256": sha256_file(a.image),
        "kernel_payload_sha256": payload_sha,
        "component_sha256": {x.name: sha256_file(x) for x in parts},
        "checks": ["ARM64 BootShim header", "inherited FD size",
                   "Android boot v4 header", "exact component concat",
                   "packaged payload SHA256", "empty GKI signature placeholder", "64MiB preliminary size limit"]
    }
    a.manifest.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: {a.image.name} validated structurally; NOT HARDWARE VERIFIED")
    print(f"SHA256: {summary['boot_image_sha256']}")

if __name__ == "__main__":
    try:
        main()
    except (AssertionError, OSError, ValueError, struct.error) as e:
        print(f"FAIL: structural verification: {e}", file=sys.stderr)
        sys.exit(1)
