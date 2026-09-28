#!/usr/bin/env python3
"""Guard the conservative CP2A BootShim relocation audit."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"Platforms/AuroraPkg/Research/cp2a_bootshim_relocation_audit.json"

def n(x): return int(x,16)

def overlap(a0,a1,b0,b1): return a0 < b1 and b0 < a1

def check(d):
    s=n(d["current_bootshim"]["relocation_destination"])
    e=n(d["current_bootshim"]["relocation_end"])
    size=n(d["current_bootshim"]["fd_size"])
    assert s+size==e==0x5ff00000
    assert s==0x5fc41000
    assert n(d["uploaded_cp2a_boot"]["arm64_text_offset"])==0
    assert n(d["uploaded_cp2a_boot"]["arm64_image_size"])==0x23a0000

    known=[d["observed_fixed_reserved_evidence"]["splash"],
           d["observed_fixed_reserved_evidence"]["dfps"],
           d["observed_fixed_reserved_evidence"]["next_historical_fixed_region"]]
    assert all(not overlap(s,e,n(a),n(b)) for a,b in known)

    i=d["interpretation"]
    assert i["known_fixed_region_overlap_observed"] is False
    assert i["relocation_verified"] is False
    assert i["hardware_boot_approved"] is False
    assert len(d["required_next_evidence"])>=2
    return True

if __name__=="__main__":
    check(json.loads(P.read_text()))
    print("PASS: no overlap with the limited fixed-region evidence; 0x5FC41000 relocation remains UNVERIFIED")
