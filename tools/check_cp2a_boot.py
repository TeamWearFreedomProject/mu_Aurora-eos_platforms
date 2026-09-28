#!/usr/bin/env python3
"""Guard derived CP2A stock boot facts and inherited bootstrap mismatch."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"Platforms/AuroraPkg/Research/supplied_cp2a_boot.json"
BOOTSTRAP=ROOT/"ImageResources/bootstrap.bin"
def check(d):
    assert d["boot_image_sha256"]=="01c93386c44e7e0637c09b24340797d4dbca4986717ba2912f278f991c8ff3c1"
    assert d["build_fingerprint"]=="google/aurora/aurora:17/CP2A.260603.001.S1/15396605:user/release-keys"
    assert d["android_boot_header_version"]==4
    assert d["kernel_size_bytes"]==36731392
    assert d["boot_signature_size_bytes"]==0
    assert d["kernel_sha256"]=="0ab5d6680d061f3d36f34078668aa2f14f08a5da729e31c19553554f4cbd3b42"
    assert d["comparison_to_supplied_cp1a"]["kernel_size_delta_bytes"]==65536
    assert d["comparison_to_supplied_cp1a"]["kernel_identical"] is False
    assert BOOTSTRAP.stat().st_size==35520512
    assert BOOTSTRAP.stat().st_size != d["kernel_size_bytes"]
    assert d["inherited_repo_bootstrap"]["exact_stock_cp2a_kernel_match"] is False
    assert d["implications"]["bootshim_relocation_verified"] is False
    assert d["implications"]["hardware_boot_approved"] is False
    return True
if __name__=="__main__":
    check(json.loads(DATA.read_text()))
    print("PASS: uploaded CP2A boot identified; inherited bootstrap is NOT the stock CP2A kernel; relocation still UNVERIFIED")
