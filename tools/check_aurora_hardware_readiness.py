#!/usr/bin/env python3
"""Consolidated offline Aurora readiness consistency gate.

This script intentionally keeps hardware_boot_approved false. Passing CI means
our evidence ledger is internally consistent, not that hardware testing is safe.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"Platforms/AuroraPkg/Research/aurora_hardware_readiness.json"
REL=ROOT/"Platforms/AuroraPkg/Research/cp2a_bootshim_relocation_audit.json"
TARGET=ROOT/"Platforms/AuroraPkg/Research/target_cp2a_verification.json"
FADT=ROOT/"Platforms/AuroraPkg/Research/cp2a_fadt_audit.json"
INF=ROOT/"Platforms/AuroraPkg/AcpiTables/AcpiTables.inf"

def check(d):
    assert d["readiness"]=="HARDWARE_PROGRESS_OBSERVED_NOT_STABLE_BOOT"
    assert d["hardware_boot_approved"] is False
    ids={x["id"] for x in d["unresolved_blockers"]}
    assert ids=={"BOOTSHIM_RELOCATION","BOOTSTRAP_COMPATIBILITY","LIVE_TARGET_IDENTITY","UEFI_RUNTIME_STALL","RECOVERY_PATH"}
    assert d["offline_checks"]["inherited_seluna_acpi_active_count"]==0
    assert d["offline_checks"]["unevidenced_msi_frame_active"] is False
    assert d["offline_checks"]["unevidenced_fadt_reset_register_active"] is False
    assert d["offline_checks"]["cp2a_pptt_topology"]=="PASS_CONSERVATIVE_DT_EVIDENCE_ONLY"
    assert d["latest_evidence"]["hardware_fastboot_candidate_test"] is True
    assert d["latest_evidence"]["ufp_usb_enumeration_045e_066b"] is True
    assert d["offline_checks"]["hardware_fastboot_transport_acceptance"]=="OBSERVED_OK_ON_2026-09-29_TEST"
    assert d["offline_checks"]["post_handoff_usb_mode"]=="UFP_LIKE_045E_066B"

    rel=json.loads(REL.read_text())
    assert rel["interpretation"]["relocation_verified"] is False
    assert rel["interpretation"]["hardware_boot_approved"] is False

    target=json.loads(TARGET.read_text())
    assert target["hardware_boot_approved"] is False
    assert target["unverified"]["watch2_bootstrap_compatibility"] is True
    assert target["unverified"]["bootshim_relocation_memory"] is True
    assert target["unverified"]["recovery_and_partition_backup"] is True

    fadt=json.loads(FADT.read_text())
    assert fadt["implications"]["reset_register_exposed"] is False

    inf=INF.read_text()
    assert "SelunaACPI/" not in inf
    return True

if __name__=="__main__":
    check(json.loads(P.read_text()))
    print("HARDWARE PROGRESS: candidate left fastboot and reached UFP-like USB; console/stability/relocation-safety/recovery remain unresolved")
