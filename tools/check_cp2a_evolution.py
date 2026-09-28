#!/usr/bin/env python3
"""Regression checks for the derived CP1A -> CP2A DTBO evolution facts."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"Platforms/AuroraPkg/Research/cp1a_cp2a_dtbo_evolution.json"
def check(d):
    assert d["coverage"]["overlay_count"] == 11
    assert d["coverage"]["identical_diff_pattern_across_all_overlays"] is True
    assert d["coverage"]["changed_properties_per_overlay"] == 15
    assert d["coverage"]["added_nodes_per_overlay"] == 5
    assert d["coverage"]["removed_nodes_per_overlay"] == 0
    r=d["first_boot_relevance"]
    assert r["reserved_memory_fixed_overrides"] == "UNCHANGED_CP1A_TO_CP2A"
    assert r["splash_framebuffer_reserved_range"] == "UNCHANGED_0x5c000000_0x5cf00000"
    assert r["bootshim_relocation"].endswith("UNVERIFIED")
    assert d["cp2a_gpio_facts"]["pin"] == "gpio19"
    return True
if __name__=="__main__":
    check(json.loads(P.read_text()))
    print("PASS: CP1A->CP2A DTBO evolution facts preserved; BootShim/bootstrap remain UNVERIFIED")
