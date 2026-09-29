#!/usr/bin/env python3
"""Guard CP2A IOMMU evidence and ensure the known-wrong inherited IORT stays quarantined."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"Platforms/AuroraPkg/Research/cp2a_iommu_audit.json"
INF=ROOT/"Platforms/AuroraPkg/AcpiTables/AcpiTables.inf"

def check(d):
    assert d["source_vendor_kernel_boot_sha256"]=="ea6d8e296cdd66fbb356f1b1563f1ed393b089b3c08e0e5215bcc74a88e47d98"
    s=d["smmu"]
    assert s[0]["reg"][0]==["0x0c600000","0x00080000"]
    assert s[0]["global_interrupt_spi"]==81
    assert s[0]["context_interrupt_count"]==64
    assert s[1]["reg"][0]==["0x059a0000","0x00010000"]
    assert s[1]["global_interrupt_spi"]==163
    assert s[1]["context_interrupt_count"]==8
    assert d["dt_iommus_summary"]["node_count_with_iommus_property"]==29
    assert d["dt_iommus_summary"]["total_mapping_tuples"]==36
    assert d["iort_status"]["inherited_seluna_iort_selected"] is False
    assert d["iort_status"]["local_iort_generated"] is False
    assert d["hardware_boot_approved"] is False

    text=INF.read_text()
    assert "IORT.aml" not in text
    assert "SelunaACPI/" not in text
    return True

if __name__=="__main__":
    check(json.loads(P.read_text()))
    print("PASS: CP2A SMMU/stream-ID evidence recorded; wrong Seluna IORT quarantined; local IORT remains intentionally absent")
