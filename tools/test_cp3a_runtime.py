"""Synthetic snapshot regression tests; no real watch or firmware required."""
import json
import struct
import tempfile
import unittest
from pathlib import Path
import audit_cp3a_runtime as tool

class TestRuntimeAudit(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        (self.path / "metadata.json").write_text(json.dumps({
            "device": "aurora", "fingerprint": tool.EXPECTED_FP
        }), encoding="utf-8")
        self.dt = self.path / "reserved-memory"
        self.dt.mkdir()
        (self.dt / "#address-cells").write_bytes((2).to_bytes(4, "big"))
        (self.dt / "#size-cells").write_bytes((2).to_bytes(4, "big"))

    def add_fixed(self, name, start, size):
        node = self.dt / name
        node.mkdir()
        (node / "reg").write_bytes(struct.pack(">IIII",
                 start >> 32, start & 0xffffffff, size >> 32, size & 0xffffffff))
        return node

    def test_known_splash_still_inconclusive(self):
        self.add_fixed("splash@5c000000", 0x5c000000, 0xf00000)
        r = tool.audit(self.path)
        self.assertEqual(r["verdict"], "INCONCLUSIVE_NO_OBSERVED_STATIC_CONFLICTS")
        self.assertFalse(r["hardware_boot_approved"])

    def test_overlap_uefi_fd_detected(self):
        self.add_fixed("reserved@5fc41000", 0x5fc41000, 0x10000)
        r = tool.audit(self.path)
        self.assertEqual(r["verdict"], "CONFLICTS_OBSERVED")
        self.assertTrue(any(x["uefi_region"] == "UEFI FD"
                        for x in r["observed_conflicts_with_inherited_uefi_map"]))

    def test_overlap_heap_detected(self):
        self.add_fixed("reserved@55710000", 0x55710000, 0x10000)
        r = tool.audit(self.path)
        self.assertTrue(any(x["uefi_region"] == "DXE Heap"
                        for x in r["observed_conflicts_with_inherited_uefi_map"]))

    def test_dynamic_region_address_not_inferred(self):
        self.add_fixed("splash", 0x5c000000, 0xf00000)
        pool = self.dt / "linux,cma"
        pool.mkdir()
        (pool / "size").write_bytes(struct.pack(">II", 0, 0x2000000))
        r = tool.audit(self.path)
        self.assertEqual(r["dynamic_reservation_nodes_unknown_addresses"], ["linux,cma"])

    def test_wrong_firmware_fails(self):
        self.add_fixed("splash", 0x5c000000, 0xf00000)
        (self.path / "metadata.json").write_text(json.dumps({
            "device": "aurora", "fingerprint": tool.EXPECTED_FP.replace("CP3A", "CP1A")
        }), encoding="utf-8")
        with self.assertRaises(ValueError):
            tool.audit(self.path)

    def test_malformed_reg_fails(self):
        node = self.dt / "bad"
        node.mkdir()
        (node / "reg").write_bytes(b"short")
        with self.assertRaises(ValueError):
            tool.audit(self.path)

    def test_multirange_reg(self):
        data = struct.pack(">IIIIIIII",
                 0, 0x5c000000, 0, 0xf00000, 0, 0x5cf00000, 0, 0x100000)
        self.assertEqual(tool.parse_reg(data, 2, 2),
                         [(0x5c000000, 0x5cf00000), (0x5cf00000, 0x5d000000)])

if __name__ == "__main__":
    unittest.main()
