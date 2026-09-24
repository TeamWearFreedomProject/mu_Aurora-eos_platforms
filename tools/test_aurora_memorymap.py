"""Regression checks for Aurora's historical fixed reservation validation."""
import json
import pathlib
import unittest
import check_aurora_memorymap as audit

class MemoryMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = audit.MAP.read_text(encoding="utf-8")
        cls.regions = json.loads(audit.FIXTURE.read_text(encoding="utf-8"))
        cls.recent_dtbo = json.loads(audit.RECENT_DTBO_FIXTURE.read_text(encoding="utf-8"))

    def test_historical_regions_protected(self):
        self.assertEqual(audit.verify(self.original, self.regions), 17)

    def test_supplied_dtbo_fixed_overrides_protected(self):
        self.assertEqual(audit.verify(self.original, self.recent_dtbo), 6)

    def test_detects_new_dtbo_modem_expansion(self):
        # The old DTS ended its modem reservation at 0x50900000.
        # The supplied DTBO extends it to 0x52900000, with video + ADSP
        # relocated accordingly. Losing the conservative PIL range is unsafe.
        changed = self.original.replace(
            '0x4AB00000, 0x0AC00000, AddMem, MEM_RES',
            '0x4AB00000, 0x05E00000, AddMem, MEM_RES')
        self.assertNotEqual(changed, self.original)
        with self.assertRaises(ValueError):
            audit.verify(changed, self.recent_dtbo)

    def test_rejects_unverified_dtbo_fixture(self):
        tampered = dict(self.recent_dtbo)
        tampered["dtbo_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            audit.verify(self.original, tampered)

    def test_detects_accidental_wlan_allocation(self):
        changed = self.original.replace(
            '0x46200000, 0x00100000, AddMem, MEM_RES, SYS_MEM_CAP, Reserv',
            '0x46200000, 0x00100000, AddMem, SYS_MEM, SYS_MEM_CAP, Conv')
        self.assertNotEqual(changed, self.original)
        with self.assertRaises(ValueError):
            audit.verify(changed, self.regions)

    def test_detects_accidental_xbl_allocation(self):
        changed = self.original.replace(
            '0x45E00000, 0x00200000, AddMem, MEM_RES, SYS_MEM_CAP, Reserv',
            '0x45E00000, 0x00200000, AddMem, SYS_MEM, SYS_MEM_CAP, BsData')
        self.assertNotEqual(changed, self.original)
        with self.assertRaises(ValueError):
            audit.verify(changed, self.regions)

if __name__ == "__main__":
    unittest.main()
