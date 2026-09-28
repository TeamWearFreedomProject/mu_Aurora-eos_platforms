#!/usr/bin/env python3
"""Static CP2A SoC audit for Aurora UEFI. Does not establish boot safety."""
import json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"Platforms/AuroraPkg/Research/cp2a_soc_audit.json"
DSC=ROOT/"Platforms/AuroraPkg/AuroraQcom.dsc.inc"
MAP=ROOT/"Platforms/AuroraPkg/Library/PlatformMemoryMapLib/PlatformMemoryMapLib.c"
CFG=ROOT/"Platforms/AuroraPkg/Library/PlatformConfigurationMapLib/PlatformConfigurationMapLib.c"

ENTRY=re.compile(r'\{\s*"([^"]+)"\s*,\s*(0x[0-9A-Fa-f]+)\s*,\s*(0x[0-9A-Fa-f]+)')

def pcd(text, name):
    m=re.search(re.escape(name)+r'\|([^\s#]+)',text)
    if not m:
        raise ValueError("missing PCD: "+name)
    return int(m.group(1),0)

def cfg(text,name):
    m=re.search(r'\{"'+re.escape(name)+r'"\s*,\s*(0x[0-9A-Fa-f]+|\d+)\}',text)
    if not m:
        raise ValueError("missing config: "+name)
    return int(m.group(1),0)

def map_entries(text):
    return {n:(int(a,16),int(l,16)) for n,a,l in ENTRY.findall(text)}

def covers(entry,start,length):
    a,l=entry
    return a <= start and a+l >= start+length

def check(d):
    dsc=DSC.read_text()
    mm=map_entries(MAP.read_text())
    c=CFG.read_text()

    assert pcd(dsc,"gArmTokenSpaceGuid.PcdGicDistributorBase")==0x0f200000
    assert pcd(dsc,"gArmTokenSpaceGuid.PcdGicRedistributorsBase")==0x0f300000
    assert pcd(dsc,"gArmTokenSpaceGuid.PcdArmArchTimerFreqInHz")==19200000
    assert pcd(dsc,"gSelunaPkgTokenSpaceGuid.PcdUartSerialBase")==0x04a98000
    assert pcd(dsc,"gArmPlatformTokenSpaceGuid.PcdCoreCount")==4
    assert pcd(dsc,"gArmPlatformTokenSpaceGuid.PcdClusterCount")==1
    assert "AuroraPkg/Library/PlatformConfigurationMapLib/PlatformConfigurationMapLib.inf" in dsc

    assert cfg(c,"MaxCoreCnt")==4
    assert cfg(c,"NumActiveCores")==4
    assert cfg(c,"NumCpus")==4

    expected={
      "TLMM_REG":(0x00500000,0x00300000),
      "GCC CLK CTL":(0x01410000,0x001e0000),
      "PMIC ARB SPMI":(0x01c40000,0x02360000),
      "QUPV3_0_QUPV3_ID_1":(0x04a98000,0x0003a000),
      "USB30_PRIM":(0x04e00000,0x00100000),
      "VENUS":(0x05a00000,0x00200000),
      "MDSS":(0x05e00000,0x00120000),
      "DISP_CC_DISP_CC":(0x05f00000,0x00020000),
      "SMMU":(0x0c600000,0x001f2020),
      "APSS_WDT_TMR1":(0x0f017000,0x00001000),
      "QTIMER":(0x0f120000,0x00001000),
      "APSS_GIC500_GICD":(0x0f200000,0x00010000),
      "APSS_GIC500_GICR":(0x0f300000,0x00100000),
    }
    for name,(start,length) in expected.items():
        assert name in mm and covers(mm[name],start,length), f"{name} no longer covers CP2A DTB MMIO"

    assert d["cpu"]["dtb_cpu_count"]==4
    assert d["cpu"]["dtb_mpidr_values"]==["0x0","0x1","0x2","0x3"]
    assert d["gic"]["aurora_memory_map_exact_match"] is True
    assert d["uart"]["pcd_base_exact_match"] is True
    assert d["timer"]["cp2a_dtb_interrupt_encoding_matches_inherited_gtdt"] is False
    assert d["mmio_corrections"]["vidc_venus_window_expanded"] is True
    assert d["mmio_corrections"]["previous"] == ["0x05a00000","0x000f0000"]
    assert d["mmio_corrections"]["cp2a"] == ["0x05a00000","0x00200000"]

    a=d["inherited_acpi_blockers"]
    assert a["apic_cpu_mpidr_match"] is False
    assert a["gtdt_timer_interrupt_match"] is False
    assert a["status"]=="APIC_GTDT_LOCALLY_PORTED_OTHER_ACPI_AND_MSI_STILL_UNVERIFIED"
    assert d["aurora_acpi_port"]["local_apic_generated"] is True
    assert d["aurora_acpi_port"]["local_gtdt_generated"] is True
    assert d["hardware_boot_approved"] is False
    return True

if __name__=="__main__":
    check(json.loads(DATA.read_text()))
    print("PASS: CP2A GIC/UART/MMIO coverage verified; CPU count corrected; inherited ACPI IRQ/MPIDR mismatches remain BLOCKERS")
