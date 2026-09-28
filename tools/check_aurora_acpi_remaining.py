#!/usr/bin/env python3
"""Guard the remaining inherited-ACPI audit for Aurora CP2A."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"Platforms/AuroraPkg/Research/cp2a_remaining_acpi_audit.json"
INF=ROOT/"Platforms/AuroraPkg/AcpiTables/AcpiTables.inf"

def check(d):
    s=d["selected_tables"]
    assert s["local_cp2a_derived"]==["APIC/MADT","GTDT"]
    assert all(x in s["inherited"] for x in ("IORT","PPTT","MCFG"))

    a=d["inherited_table_audit"]
    assert a["DSDT"]["hardware_blocker"] is False
    assert a["DBG2"]["cp2a_uart_base_match"] is True
    assert a["DBG2"]["cp2a_usb_mmio_match"] is True

    assert a["PPTT"]["hardware_blocker"] is True
    assert a["PPTT"]["inherited_all_cpu_nodes_share_private_cache_offsets"]==["0x8e","0xa6"]
    assert len(a["PPTT"]["cp2a_distinct_l1_phandles"])==8

    assert a["IORT"]["hardware_blocker"] is True
    assert a["IORT"]["inherited_smmu_bases"]==["0x15000000","0x02ca0000"]
    assert a["IORT"]["cp2a_smmu_bases"]==["0x059a0000","0x0c600000"]
    assert a["IORT"]["exact_base_match_count"]==0

    assert a["MCFG"]["hardware_blocker"] is True
    assert a["MCFG"]["cp2a_base_dtb_pci_or_pcie_nodes"]==0

    sep=d["separation_status"]
    assert sep["cpu_interrupt_core_localized"] is True
    assert sep["platform_peripheral_acpi_localized"] is False
    assert sep["next_priority"]=="IORT"
    assert d["hardware_boot_approved"] is False

    text=INF.read_text()
    assert "Generated/APIC.aml" in text and "Generated/GTDT.aml" in text
    for inherited in ("IORT.aml","PPTT.aml","MCFG.aml"):
        assert inherited in text
    return True

if __name__=="__main__":
    check(json.loads(P.read_text()))
    print("PASS: APIC/GTDT are Aurora-local; inherited IORT/PPTT/MCFG remain explicit blockers; hardware boot NOT approved")
