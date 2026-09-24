#!/usr/bin/env python3
"""Confirm exact observed CP3A target and preserve research-only warning."""
import json
from pathlib import Path
TARGET = Path(__file__).resolve().parents[1] / "Platforms/AuroraPkg/Research/target_cp3a_verification.json"
def check(d):
    assert d["device"] == "aurora"
    assert d["current_fingerprint"] == "google/aurora/aurora:17/CP3A.260905.002.E1/16053217:user/release-keys"
    assert d["bootloader_observed"] == "eos-6.08-15857178"
    assert d["status"] == "RESEARCH_ONLY_DO_NOT_BOOT_DO_NOT_FLASH"
    assert len(d["verified"]) == 9 and all(x is False for x in d["verified"].values())
    assert "CP3A provenance unverified" in d["dtbo_reference_warning"]
    return len(d["verified"])
if __name__ == "__main__":
    print(f"PASS: CP3A target recorded; {check(json.loads(TARGET.read_text()))} hardware compatibility items UNVERIFIED")
