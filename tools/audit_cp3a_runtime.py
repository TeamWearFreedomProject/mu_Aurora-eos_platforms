#!/usr/bin/env python3
"""Read-only audit of a running CP3A aurora's reserved-memory DT subtree.

The device-tree filesystem represents Linux's effective view, not every
early bootloader, TrustZone or dynamic allocation. Never authorizes boot.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import struct
from check_aurora_memorymap import MAP, parse as parse_uefi_map

EXPECTED_FP = "google/aurora/aurora:17/CP3A.260905.002.E1/16053217:user/release-keys"
UEFI_OBJECT_NAMES = (
    "FV Region", "ABOOT FV", "UEFI FD", "SEC Heap", "CPU Vectors",
    "MMU PageTables", "UEFI Stack", "Log Buffer", "Info Blk",
    "Sched Heap", "DXE Heap",
)

def cell_count(path: Path, label: str) -> int:
    if not path.is_file():
        raise ValueError(f"missing {label}: {path}")
    data = path.read_bytes()
    if len(data) != 4:
        raise ValueError(f"{label} is not one big-endian 32-bit cell")
    value = int.from_bytes(data, "big")
    if value not in (1, 2):
        raise ValueError(f"unsupported {label}: {value}")
    return value

def parse_reg(raw: bytes, address_cells: int, size_cells: int):
    count = address_cells + size_cells
    stride = count * 4
    if not raw or len(raw) % stride:
        raise ValueError("reg length incompatible with DT address/size cells")
    ints = struct.unpack(">" + "I" * (len(raw) // 4), raw)
    values = []
    for pos in range(0, len(ints), count):
        addr = size = 0
        for cell in ints[pos:pos + address_cells]:
            addr = (addr << 32) | cell
        for cell in ints[pos + address_cells:pos + count]:
            size = (size << 32) | cell
        if size == 0 or addr + size > (1 << 64):
            raise ValueError("zero or overflowing DT reg range")
        values.append((addr, addr + size))
    return values

def parse_live_tree(root: Path):
    if not root.is_dir():
        raise ValueError(f"reserved-memory directory missing: {root}")
    ac = cell_count(root / "#address-cells", "address cells")
    sc = cell_count(root / "#size-cells", "size cells")
    fixed, dynamic = [], []
    for node in sorted(root.iterdir(), key=lambda n: n.name):
        if not node.is_dir():
            continue
        reg, size = node / "reg", node / "size"
        if reg.is_file():
            for start, end in parse_reg(reg.read_bytes(), ac, sc):
                fixed.append({"node": node.name, "start": start, "end": end,
                              "no_map": (node / "no-map").is_file()})
        elif size.is_file():
            dynamic.append(node.name)
    if not fixed:
        raise ValueError("no fixed reserved-memory nodes; snapshot incomplete")
    return fixed, dynamic

def overlaps(a, b):
    return a["start"] < b["end"] and b["start"] < a["end"]

def format_range(region):
    return f"0x{region['start']:016x}..0x{region['end']:016x}"

def audit(snapshot: Path, *, memory_source: Path = MAP):
    metadata_file = snapshot / "metadata.json"
    if not metadata_file.is_file():
        raise ValueError("metadata.json absent; use the CP3A read-only collector")
    metadata = json.loads(metadata_file.read_text(encoding="utf-8-sig"))
    if metadata.get("device") != "aurora" or metadata.get("fingerprint") != EXPECTED_FP:
        raise ValueError("not the observed Aurora CP3A build: never mix firmware versions")
    fixed, dynamic = parse_live_tree(snapshot / "reserved-memory")
    entries = parse_uefi_map(memory_source.read_text(encoding="utf-8"))
    alloc = [e for e in entries if e["resource"] == "SYS_MEM" and
             e["kind"] in ("Conv", "BsData", "RtData", "BsCode", "RtCode") and
             e["hob"] in ("AddMem", "NoHob")]
    planned = [e for e in entries if e["name"] in UEFI_OBJECT_NAMES]
    conflicts = []
    for f in fixed:
        for e in alloc:
            if overlaps(f, e):
                conflicts.append({"dt_node": f["node"], "dt_range": format_range(f),
                                  "uefi_region": e["name"], "uefi_range": format_range(e),
                                  "kind": "reserve_vs_allocatable"})
        for e in planned:
            if e not in alloc and overlaps(f, e):
                conflicts.append({"dt_node": f["node"], "dt_range": format_range(f),
                                  "uefi_region": e["name"], "uefi_range": format_range(e),
                                  "kind": "reserve_vs_planned_uefi"})
    safe_region_data = [{"node": f["node"], "range": format_range(f),
                         "no_map": f["no_map"]} for f in fixed]
    return {
        "target": "aurora CP3A.260905.002.E1",
        "source": "running Linux's DTFS reserved-memory subtree, read-only adb pull",
        "fixed_regions": safe_region_data,
        "dynamic_reservation_nodes_unknown_addresses": dynamic,
        "observed_conflicts_with_inherited_uefi_map": conflicts,
        "bootshim_relocation_base_inherited": "0x5fc41000",
        "verdict": "CONFLICTS_OBSERVED" if conflicts else "INCONCLUSIVE_NO_OBSERVED_STATIC_CONFLICTS",
        "hardware_boot_approved": False,
        "still_unknown": ["pre-Linux bootloader memory ownership",
                          "TrustZone carve-outs", "SMEM RAM partition table",
                          "dynamic pool allocation", "selected early-boot DTB",
                          "Watch 2 ACPI and bootstrap compatibility"],
        "warning": "DO NOT FLASH/FASTBOOT BOOT. No observed conflict is not proof of safe relocation."
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path,
                        help="output folder from collect_cp3a_memory.ps1")
    parser.add_argument("--output", type=Path,
                        help="optional privacy-limited JSON report file")
    args = parser.parse_args()
    try:
        report = audit(args.snapshot)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(2, f"ERROR: {error}\n")
    output = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 1 if report["observed_conflicts_with_inherited_uefi_map"] else 0

if __name__ == "__main__":
    raise SystemExit(main())
