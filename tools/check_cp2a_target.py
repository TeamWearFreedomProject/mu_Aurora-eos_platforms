#!/usr/bin/env python3
"""Guard the current CP2A research target without pretending there is a live ADB measurement."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"Platforms/AuroraPkg/Research/target_cp2a_verification.json"

def check(d):
    assert d["device"]=="aurora"
    assert d["target_build"]=="CP2A.260603.001.S1"
    assert d["target_fingerprint"]=="google/aurora/aurora:17/CP2A.260603.001.S1/15396605:user/release-keys"
    assert d["status"]=="RESEARCH_ONLY_DO_NOT_BOOT_DO_NOT_FLASH"
    assert all(d["verified_from_uploaded_cp2a_images"].values())
    assert all(d["unverified"].values())
    assert d["hardware_boot_approved"] is False
    assert d["previous_live_observation"]["firmware"]=="CP3A.260905.002.E1"
    return True

if __name__=="__main__":
    check(json.loads(P.read_text()))
    print("PASS: CP2A is the research target from uploaded artifacts; live CP2A state and boot safety remain UNVERIFIED")
