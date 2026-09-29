#!/usr/bin/env python3
"""Guard the redacted 2026-09-29 real-hardware UFP observation."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"Platforms/AuroraPkg/Research/hardware_observation_2026-09-29_ufp.json"

def check(d):
    assert d["candidate"]["source_commit"]=="239711b777f94da4713395c6c90c52c02dfce11c"
    assert d["candidate"]["persistent_flash_performed"] is False
    h=d["host_observation"]
    assert h["fastboot_send_result"]=="OKAY"
    assert h["fastboot_boot_result"]=="OKAY"
    assert h["windows_usb"]["vid"]=="0x045e"
    assert h["windows_usb"]["pid"]=="0x066b"
    assert h["windows_usb"]["driver"]=="winusb.inf"
    assert h["windows_usb"]["service"]=="WINUSB"
    assert h["windows_usb"]["matching_device_id"]=="USB\\MS_COMP_WINUSB"
    assert h["windows_usb"]["problem_code"]==0
    assert h["windows_usb"]["is_present"] is True
    assert h["windows_usb"]["has_problem"] is False
    assert "USB\\COMPAT_VID_045E&Class_FF&SubClass_FF&Prot_FF" in h["windows_usb"]["compatible_ids"]
    assert h["windows_usb"]["instance_specific_serial_redacted"] is True
    c=d["source_correlation"]
    assert c["in_tree_fastboot_descriptor"]["pid"]=="0x0c2f"
    assert c["in_tree_ufp_binary"]["little_endian_vid_pid_occurrences"]==2
    i=d["interpretation"]
    assert i["device_left_fastboot_transport"] is True
    assert i["ufp_like_usb_enumeration_observed"] is True
    assert i["strong_evidence_candidate_reached_uefi_ufp_stage"] is True
    assert i["full_uefi_console_or_frontpage_observed"] is False
    assert i["relocation_memory_safety_proven"] is False
    assert i["hardware_boot_approved"] is False
    return True

if __name__=="__main__":
    check(json.loads(P.read_text()))
    print("PASS: redacted hardware observation records UFP-like 045E:066B handoff without claiming stable/safe boot")
