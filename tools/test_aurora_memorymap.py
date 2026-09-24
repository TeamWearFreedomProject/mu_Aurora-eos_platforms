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

    def test_historical_regions_protected(self):
        self.assertEqual(audit.verify(self.original, self.regions), 17)

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
