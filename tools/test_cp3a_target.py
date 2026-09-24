import copy
import json
import unittest
import check_cp3a_target as gate
class TestCP3A(unittest.TestCase):
    def setUp(self):
        self.d = json.loads(gate.TARGET.read_text())
    def test_research_only(self):
        self.assertEqual(gate.check(self.d),9)
    def test_wrong_build(self):
        d=copy.deepcopy(self.d)
        d["current_fingerprint"]=d["current_fingerprint"].replace("CP3A","CP1A")
        with self.assertRaises(AssertionError):
            gate.check(d)
    def test_unreviewed_hardware_claim(self):
        d=copy.deepcopy(self.d)
        d["verified"]["bootshim_relocation_memory"]=True
        with self.assertRaises(AssertionError):
            gate.check(d)
if __name__ == "__main__":
    unittest.main()
