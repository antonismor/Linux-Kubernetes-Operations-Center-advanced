import unittest
from lkoc.core import safe_name,parse_quantity
class CoreTests(unittest.TestCase):
    def test_safe_name(self):self.assertEqual(safe_name('prod cluster'),'prod-cluster')
    def test_cpu(self):self.assertEqual(parse_quantity('500m'),0.5)
    def test_memory(self):self.assertEqual(parse_quantity('1Gi'),1024**3)
if __name__=='__main__':unittest.main()
