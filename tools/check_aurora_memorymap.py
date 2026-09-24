#!/usr/bin/env python3
"""Check experimental Aurora map against *historical* extracted fixed regions."""
from __future__ import annotations
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MAP = ROOT / "Platforms/AuroraPkg/Library/PlatformMemoryMapLib/PlatformMemoryMapLib.c"
FIXTURE = ROOT / "Platforms/AuroraPkg/Research/early_pw2_reserved_regions.json"
ENTRY = re.compile(
    r'^\s*\{\s*"(?P<name>[^"]+)"\s*,\s*'
    r'(?P<start>0x[0-9a-fA-F]+)\s*,\s*(?P<length>0x[0-9a-fA-F]+)\s*,\s*'
    r'(?P<hob>\w+)\s*,\s*(?P<resource>\w+)\s*,\s*\w+\s*,\s*'
    r'(?P<kind>\w+)\s*,', re.M)

def parse(text: str):
    result = []
    for m in ENTRY.finditer(text):
        d = m.groupdict()
        result.append({
            "name": d["name"], "start": int(d["start"], 16),
            "end": int(d["start"], 16) + int(d["length"], 16),
            "hob": d["hob"], "resource": d["resource"], "kind": d["kind"]
        })
    if len(result) < 30:
        raise ValueError("Memory map parsed too few descriptors")
    return result

def verify(text: str, data: dict):
    entries = parse(text)
    if data.get("source_commit") != "e3d5fc73b4c97ea19ae5a0fd1d4eee1324703ad0":
        raise ValueError("historical source revision changed without review")
    protected = sorted(
        (e for e in entries if e["kind"] == "Reserv" and
         e["resource"] in ("MEM_RES", "SYS_MEM") and
         e["hob"] in ("NoHob", "AddMem")),
        key=lambda e: e["start"])
    allocatable = [e for e in entries if e["kind"] in
                   ("Conv", "BsData", "RtData", "BsCode", "RtCode") and
                   e["resource"] == "SYS_MEM" and e["hob"] in ("AddMem", "NoHob")]
    if len(data.get("fixed_regions", [])) < 17:
        raise ValueError("expected historical carve-out fixture incomplete")

    for region in data["fixed_regions"]:
        start = int(region["start"], 16)
        end = start + int(region["length"], 16)
        if end <= start:
            raise ValueError(f"invalid range: {region['name']}")
        for e in allocatable:
            if start < e["end"] and e["start"] < end:
                raise ValueError(f"{region['name']} intersects allocatable {e['name']}")
        cursor = start
        for e in protected:
            if e["start"] <= cursor < e["end"]:
                cursor = e["end"]
                if cursor >= end:
                    break
        if cursor < end:
            raise ValueError(f"unprotected historical fixed area: {region['name']} "
                             f"at 0x{cursor:x}")

    framebuffers = [e for e in entries if e["name"] == "Display Reserved"]
    if len(framebuffers) != 1 or framebuffers[0]["start"] != 0x5C000000 or (
       framebuffers[0]["end"] != 0x5CF00000):
        raise ValueError("SimpleFbDxe named region must cover splash, not DFPS")

    fd = [e for e in entries if e["name"] == "UEFI FD"]
    if len(fd) != 1 or not (fd[0]["start"] <= 0x5FC41000 and
                           fd[0]["end"] >= 0x5FF00000):
        raise ValueError("inherited UEFI FD region inconsistent with Aurora FDF")
    # This validates only historical static carve-outs, NOT the current
    # bootloader's live allocatable memory or boot relocation safety.
    return len(data["fixed_regions"])

def main():
    try:
        n = verify(MAP.read_text(encoding="utf-8"),
                   json.loads(FIXTURE.read_text(encoding="utf-8")))
    except (ValueError, OSError, KeyError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        return 1
    print(f"PASS: {n} historical fixed regions protected; "
          "live Aurora LTE memory map STILL UNVERIFIED")
    return 0

if __name__ == "__main__":
    sys.exit(main())
