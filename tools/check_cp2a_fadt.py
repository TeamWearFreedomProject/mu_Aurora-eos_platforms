#!/usr/bin/env python3
"""Guard CP2A FADT evidence: PSCI is supported; ResetReg is still unverified."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"Platforms/AuroraPkg/Research/cp2a_fadt_audit.json"
F=ROOT/"Platforms/AuroraPkg/AcpiTables/FACP.aslc"

def check(d):
    assert d["cp2a_psci"]["compatible"]=="arm,psci-1.0"
    assert d["cp2a_psci"]["method"]=="smc"
    assert d["cp2a_psci"]["fadt_arm_boot_arch_psci_compliant_supported"] is True
    assert d["implications"]["psci_flag_verified"] is True
    assert d["implications"]["reset_register_verified"] is False
    assert d["implications"]["reset_register_exposed"] is False
    assert d["implications"]["fadt_core_conservative"] is True
    assert d["implications"]["fadt_fully_verified"] is False
    assert d["implications"]["hardware_boot_approved"] is False

    text=F.read_text()
    assert "EFI_ACPI_6_0_ARM_PSCI_COMPLIANT" in text
    assert "0x009020B4" not in text
    assert "NULL_GAS" in text
    return True

if __name__=="__main__":
    check(json.loads(P.read_text()))
    print("PASS: CP2A PSCI flag retained; unevidenced inherited ResetReg is quarantined")
