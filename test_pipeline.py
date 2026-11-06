import unittest
from pipeline import allocate_budget, distance_km, nearest_catchments, valid_coord

class BoundaryTests(unittest.TestCase):
    def test_identical_points(self):
        self.assertEqual(distance_km(33,-112,33,-112),0)
    def test_known_distance(self):
        self.assertAlmostEqual(distance_km(0,0,0,1),111.195,places=2)
    def test_cents_conservation(self):
        self.assertEqual(sum(allocate_budget({'a':1,'b':1,'c':1},100).values()),100)
    def test_zero_weight(self):
        self.assertEqual(allocate_budget({'a':0,'b':1},100)['a'],0)
    def test_invalid_budget(self):
        with self.assertRaises(ValueError): allocate_budget({'a':0},100)
    def test_overlap_deduplication(self):
        schools=[{'school_id':'s','lat':33,'lon':-112}]
        venues=[{'venue_id':'a','lat':33,'lon':-112},{'venue_id':'b','lat':33,'lon':-112}]
        self.assertEqual(len(nearest_catchments(schools,venues,10)),1)
    def test_outside_radius(self):
        self.assertEqual(nearest_catchments([{'school_id':'s','lat':35,'lon':-112}],[{'venue_id':'a','lat':33,'lon':-112}],10),[])
    def test_invalid_coordinates(self):
        self.assertFalse(valid_coord(None,-112))
        self.assertFalse(valid_coord(0,0))

if __name__=='__main__': unittest.main()
