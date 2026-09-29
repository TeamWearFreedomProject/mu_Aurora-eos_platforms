#!/usr/bin/env python3
"""Guard Aurora's minimal CP2A-local ACPI selection and quarantine policy."""
import json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"Platforms/AuroraPkg/Research/cp2a_remaining_acpi_audit.json"
INF=ROOT/"Platforms/AuroraPkg/AcpiTables/AcpiTables.inf"
DSDT=ROOT/"Platforms/AuroraPkg/AcpiTables/DSDT.asl"

def check(d):
    s=d["selected_tables"]
    assert s["local_cp2a_derived"]==["APIC/MADT","GTDT","DSDT"]
    assert s["active_inherited"]==[]
    assert set(s["quarantined_inherited"])=={
        "CSRT","DBG2","IORT","MCFG","PPTT","SSDT","TPMDev","SoftwareTpm2Table"
    }

    sep=d["separation_status"]
    assert sep["cpu_interrupt_core_localized"] is True
    assert sep["local_cpu_namespace"] is True
    assert sep["active_seluna_acpi_binary_count"]==0
    assert sep["inherited_tables_quarantined"] is True
    assert sep["platform_peripheral_acpi_localized"] is False
    assert sep["next_priority"]=="IORT_RECONSTRUCTION"
    assert d["hardware_boot_approved"] is False

    text=INF.read_text()
    assert "Generated/APIC.aml" in text and "Generated/GTDT.aml" in text
    assert "DSDT.asl" in text
    assert "SelunaACPI/" not in text
    for bad in ("CSRT.aml","DBG2.aml","IORT.aml","MCFG.aml","PPTT.aml",
                "SSDT.aml","TPMDev.dat","SoftwareTpm2Table.aml"):
        assert bad not in text

    dsdt=DSDT.read_text()
    assert len(re.findall(r"Device \(CPU[0-3]\)",dsdt))==4
    assert [int(x) for x in re.findall(r"Name \(_UID, ([0-3])\)",dsdt)]==[0,1,2,3]
    assert dsdt.count('"ACPI0007"')==4
    return True

if __name__=="__main__":
    check(json.loads(P.read_text()))
    print("PASS: active ACPI is local minimal core only; all inherited Seluna ACPI binaries quarantined; hardware boot NOT approved")
