#!/usr/bin/env python3
"""CI gate for Aurora-local CP2A MADT/GTDT generation."""
import importlib.util
import pathlib
import sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
GEN=ROOT/"tools/generate_aurora_acpi.py"
INF=ROOT/"Platforms/AuroraPkg/AcpiTables/AcpiTables.inf"

spec=importlib.util.spec_from_file_location("aurora_acpi_gen", GEN)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

apic=mod.build_apic()
gtdt=mod.build_gtdt()
mod.validate(apic,gtdt)

text=INF.read_text()
assert "Generated/APIC.aml" in text
assert "Generated/GTDT.aml" in text
assert "SelunaACPI/5100/builtin/APIC.aml" not in text
assert "SelunaACPI/5100/builtin/GTDT.aml" not in text

assert mod.CPU_MPIDRS == (0,1,2,3)
assert mod.PMU_GSIV == 22
assert mod.VGIC_GSIV == 25
assert mod.TIMER_GSIV == (17,18,19,16)
assert mod.MEMTIMER_PHYS_GSIV == 40
assert mod.MEMTIMER_VIRT_GSIV == 39

print("PASS: Aurora uses generated CP2A-local APIC/GTDT; inherited PW3 APIC/GTDT are no longer selected")
