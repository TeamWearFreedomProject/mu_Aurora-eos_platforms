#!/usr/bin/env python3
"""Guard facts derived from the uploaded CP2A init_boot/vendor_boot/boot chain."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"Platforms/AuroraPkg/Research/supplied_cp2a_boot_chain.json"

def check(d):
    assert d["fingerprint"]=="google/aurora/aurora:17/CP2A.260603.001.S1/15396605:user/release-keys"
    i=d["uploaded_init_boot"]
    assert i["sha256"]=="72503b1e0ef5cb54512d666edf1c23bb1acbf47e0b69766b7dcdb3d4c728b46d"
    assert i["android_boot_header_version"]==4
    assert i["kernel_size_bytes"]==0
    assert i["ramdisk_size_bytes"]==2618142
    assert i["boot_signature_size_bytes"]==0
    assert i["fdt_magic_occurrences"]==0

    v=d["uploaded_vendor_boot"]
    assert v["sha256"]=="72c4909328f2f4c60e49f90191cc8774334d7d59fdefb5607792a86cfceb28f6"
    assert v["vendor_boot_header_version"]==4
    assert v["page_size_bytes"]==4096
    assert v["dtb_size_bytes"]==0
    assert v["vendor_ramdisk_table"]["entry_type"]==1
    assert v["vendor_ramdisk_table"]["entry_type_name"]=="platform"
    assert v["fdt_magic_occurrences"]==0

    b=d["uploaded_cp2a_boot_dtb_check"]
    assert b["fdt_magic_occurrences"]==1
    assert b["fdt_total_size_bytes"]==72
    assert b["fdt_strings_size_bytes"]==0
    assert b["fdt_structure_size_bytes"]==16

    base=d["base_dtb_result"]
    assert all(x is False for x in base.values())
    assert d["next_evidence"].startswith("Matching CP2A vendor_kernel_boot.img")
    assert d["hardware_boot_approved"] is False
    return True

if __name__=="__main__":
    check(json.loads(P.read_text()))
    print("PASS: CP2A init_boot/vendor_boot analyzed; base DTB still missing; vendor_kernel_boot is next evidence")
