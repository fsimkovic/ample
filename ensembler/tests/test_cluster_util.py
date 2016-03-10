"""Test functions for ensembler.cluster_util.py"""

import unittest

from ample.ensembler.cluster_util import *

class Test(unittest.TestCase):
    
    def test_random_cluster(self):
        models = ["/foo/bar/model_{0}.pdb".format(i) for i in xrange(1000)]
        ########################################################################
        # Test Case 1
        max_cluster_size = 200
        num_clusters = 5
        clusters, _ = random_cluster("random", max_cluster_size, models, num_clusters)
        self.assertEqual(num_clusters, len(clusters))
        for cluster in clusters:
            self.assertEqual(max_cluster_size, len(cluster))
        ########################################################################
        # Test Case 2
        max_cluster_size = 100
        num_clusters = 1
        clusters, _ = random_cluster("random", max_cluster_size, models, num_clusters)
        self.assertEqual(num_clusters, len(clusters))
        for cluster in clusters:
            self.assertEqual(max_cluster_size, len(cluster))
        ########################################################################
        # Test Case 3
        max_cluster_size = 200
        num_clusters = 10
        clusters, _ = random_cluster("random", max_cluster_size, models, num_clusters)
        self.assertEqual(num_clusters, len(clusters))
        for cluster in clusters:
            self.assertEqual(max_cluster_size, len(cluster))
            
if __name__ == "__main__":
    unittest.main()
