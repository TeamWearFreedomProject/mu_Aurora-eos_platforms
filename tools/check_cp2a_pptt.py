#!/usr/bin/env python3
"""Guard the conservative CP2A-derived Aurora PPTT."""
import importlib.util, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"Platforms/AuroraPkg/Research/cp2a_pptt_audit.json"
INF=ROOT/"Platforms/AuroraPkg/AcpiTables/AcpiTables.inf"
GEN=ROOT/"tools/generate_aurora_acpi.py"

spec=importlib.util.spec_from_file_location("aurora_acpi_gen", GEN)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def check(d):
    assert d["cpu"]["count"]==4
    assert d["cpu"]["uids"]==[0,1,2,3]
    assert d["cpu"]["each_i_cache_size_bytes"]==32768
    assert d["cpu"]["each_d_cache_size_bytes"]==32768
    assert d["cache_topology"]["distinct_l1_instruction_nodes"]==4
    assert d["cache_topology"]["distinct_l1_data_nodes"]==4
    assert d["cache_topology"]["shared_l2_nodes"]==1
    assert d["cache_topology"]["shared_l2_size_bytes"]==524288
    assert set(d["properties_not_present_in_cp2a_dtb"])=={
        "cache-line-size","cache-sets","cache-associativity"
    }
    g=d["generated_pptt"]
    assert g["length_bytes"]==0x180
    assert g["cache_size_valid"] is True and g["cache_type_valid"] is True
    assert g["line_size_valid"] is False
    assert g["number_of_sets_valid"] is False
    assert g["associativity_valid"] is False
    assert d["inherited_seluna_pptt_selected"] is False
    assert d["hardware_boot_approved"] is False

    pptt=mod.build_pptt()
    assert len(pptt)==0x180 and pptt[:4]==b"PPTT" and (sum(pptt)&0xff)==0
    text=INF.read_text()
    assert "Generated/PPTT.aml" in text
    assert "SelunaACPI/5100/builtin/PPTT.aml" not in text
    return True

if __name__=="__main__":
    check(json.loads(P.read_text()))
    print("PASS: local PPTT models 4 distinct L1I/L1D pairs + shared 512KiB L2; unknown cache geometry remains unadvertised")
