#!/usr/bin/env python3
"""Generate Aurora-local MADT (APIC) and GTDT from verified CP2A DT evidence.

This is an offline table generator only. It does not boot or modify hardware.
"""
from __future__ import annotations
import argparse
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "Platforms/AuroraPkg/AcpiTables/Generated"

OEM_ID = b"QCOM  "
OEM_TABLE_ID = b"QCOMEDK2"
OEM_REVISION = 0x00005100
CREATOR_ID = b"QCOM"
CREATOR_REVISION = 1

# CP2A vendor_kernel_boot base-DTB facts.
CPU_MPIDRS = (0, 1, 2, 3)
GICD_BASE = 0x0F200000
GICR_BASE = 0x0F300000
GICR_LENGTH = 0x00100000

# DT GIC PPI cells are PPI-relative; architectural INTID/GSIV adds 16.
PMU_PPI = 6
GIC_MAINTENANCE_PPI = 9
PMU_GSIV = 16 + PMU_PPI                 # 22
VGIC_GSIV = 16 + GIC_MAINTENANCE_PPI   # 25

# arm,armv8-timer order: secure physical, non-secure physical, virtual, hyp.
TIMER_PPI = (1, 2, 3, 0)
TIMER_GSIV = tuple(16 + x for x in TIMER_PPI)  # 17,18,19,16
# CP2A DT uses IRQ_TYPE_LEVEL_LOW for all four architected timer PPIs.
GTDT_LEVEL_LOW_FLAGS = 0x2  # bit0 mode=level(0), bit1 polarity=active-low(1)

MEMTIMER_BASE = 0x0F120000
MEMTIMER_FRAME_BASE = 0x0F121000
MEMTIMER_FRAME_EL0_BASE = 0x0F122000
MEMTIMER_PHYS_GSIV = 32 + 8  # GIC_SPI 8 -> 40
MEMTIMER_VIRT_GSIV = 32 + 7  # GIC_SPI 7 -> 39


def acpi_header(sig: bytes, length: int, revision: int) -> bytearray:
    return bytearray(struct.pack(
        "<4sIBB6s8sI4sI",
        sig, length, revision, 0,
        OEM_ID, OEM_TABLE_ID, OEM_REVISION, CREATOR_ID, CREATOR_REVISION
    ))


def finish_checksum(table: bytearray) -> bytes:
    table[9] = 0
    table[9] = (-sum(table)) & 0xFF
    assert sum(table) & 0xFF == 0
    return bytes(table)


def build_apic() -> bytes:
    body = bytearray(struct.pack("<II", 0, 0))

    for uid, mpidr in enumerate(CPU_MPIDRS):
        body += struct.pack(
            "<BBHIIIIIQQQQIQQBBH",
            0x0B, 0x50, 0,       # GICC type/length/reserved
            uid, uid,             # CPU interface number / processor UID
            0x1,                 # enabled
            0,                   # parking protocol
            PMU_GSIV,            # performance interrupt from CP2A PMU PPI6
            0, 0, 0, 0,          # parked/GICC/GICV/GICH bases
            VGIC_GSIV,            # maintenance PPI9 -> GSIV25
            0,                    # redistributor base lives in GICR subtable
            mpidr,
            0, 0, 0
        )

    body += struct.pack(
        "<BBHIQIB3s",
        0x0C, 0x18, 0, 0, GICD_BASE, 0, 3, b"\0\0\0"
    )
    body += struct.pack(
        "<BBHQI",
        0x0E, 0x10, 0, GICR_BASE, GICR_LENGTH
    )

    # Keep the inherited MSI frame for now. CP2A base DT does not describe it,
    # so this remains explicitly UNVERIFIED rather than silently removed.
    body += struct.pack(
        "<BBHIQIHH",
        0x0D, 0x18, 0, 0, 0x0F210000, 0x1, 0x80, 0x340
    )

    length = 36 + len(body)
    table = acpi_header(b"APIC", length, 5) + body
    assert length == 0x1AC
    return finish_checksum(table)


def build_gtdt() -> bytes:
    secure, nonsecure, virt, hyp = TIMER_GSIV
    body = bytearray(struct.pack(
        "<QIIIIIIIIIQII",
        0xFFFFFFFFFFFFFFFF, 0,
        secure, GTDT_LEVEL_LOW_FLAGS,
        nonsecure, GTDT_LEVEL_LOW_FLAGS,
        virt, GTDT_LEVEL_LOW_FLAGS,
        hyp, GTDT_LEVEL_LOW_FLAGS,
        0xFFFFFFFFFFFFFFFF,
        1, 0x60
    ))

    # One memory-mapped generic timer block; CP2A DT uses level-high SPIs.
    body += struct.pack(
        "<BHBQII",
        0, 0x3C, 0,
        MEMTIMER_BASE,
        1, 0x14
    )
    body += struct.pack(
        "<B3sQQIIIII",
        0, b"\0\0\0",
        MEMTIMER_FRAME_BASE,
        MEMTIMER_FRAME_EL0_BASE,
        MEMTIMER_PHYS_GSIV, 0,
        MEMTIMER_VIRT_GSIV, 0,
        0x2
    )

    length = 36 + len(body)
    table = acpi_header(b"GTDT", length, 2) + body
    assert length == 0x9C
    return finish_checksum(table)


def validate(apic: bytes, gtdt: bytes) -> None:
    assert apic[:4] == b"APIC" and len(apic) == 0x1AC and (sum(apic) & 0xFF) == 0
    assert gtdt[:4] == b"GTDT" and len(gtdt) == 0x9C and (sum(gtdt) & 0xFF) == 0

    # GICC MPIDRs and PMU/VGIC interrupt fields.
    for i, mpidr in enumerate(CPU_MPIDRS):
        off = 44 + i * 0x50
        assert apic[off] == 0x0B and apic[off + 1] == 0x50
        assert struct.unpack_from("<I", apic, off + 20)[0] == PMU_GSIV
        assert struct.unpack_from("<I", apic, off + 56)[0] == VGIC_GSIV
        assert struct.unpack_from("<Q", apic, off + 68)[0] == mpidr

    # GICD and GICR.
    assert struct.unpack_from("<Q", apic, 0x174)[0] == GICD_BASE
    assert struct.unpack_from("<Q", apic, 0x188)[0] == GICR_BASE
    assert struct.unpack_from("<I", apic, 0x190)[0] == GICR_LENGTH

    # Architected timer GSIVs and level-low flags.
    vals = (
        struct.unpack_from("<I", gtdt, 48)[0],
        struct.unpack_from("<I", gtdt, 56)[0],
        struct.unpack_from("<I", gtdt, 64)[0],
        struct.unpack_from("<I", gtdt, 72)[0],
    )
    assert vals == TIMER_GSIV
    assert all(struct.unpack_from("<I", gtdt, x)[0] == GTDT_LEVEL_LOW_FLAGS
               for x in (52, 60, 68, 76))
    assert struct.unpack_from("<Q", gtdt, 100)[0] == MEMTIMER_BASE
    assert struct.unpack_from("<I", gtdt, 136)[0] == MEMTIMER_PHYS_GSIV
    assert struct.unpack_from("<I", gtdt, 144)[0] == MEMTIMER_VIRT_GSIV


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--check-only", action="store_true")
    a = p.parse_args()
    apic, gtdt = build_apic(), build_gtdt()
    validate(apic, gtdt)
    if not a.check_only:
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "APIC.aml").write_bytes(apic)
        (OUT / "GTDT.aml").write_bytes(gtdt)
        print(f"generated {OUT/'APIC.aml'} ({len(apic)} bytes)")
        print(f"generated {OUT/'GTDT.aml'} ({len(gtdt)} bytes)")
    print("PASS: Aurora APIC/GTDT encode CP2A CPU/GIC/PMU/timer evidence; MSI frame remains UNVERIFIED")
    return 0

if __name__ == "__main__":
    sys.exit(main())
