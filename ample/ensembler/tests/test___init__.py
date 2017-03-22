"""Test functions for ample.ensembler.__init__"""

__author__ = "Felix Simkovic"
__date__ = "22 Mar 2017"

import unittest

from ample import ensembler


class Test(unittest.TestCase):

    def test__sort_ensembles_1(self):
        ensemble_pdbs = [
            'c1_t100_r3_polyAla.pdb', 'c1_t85_r1_polyAla.pdb', 'c1_t76_r3_polyAla.pdb', 'c1_t61_r1_polyAla.pdb',
            'c1_t52_r3_polyAla.pdb', 'c1_t37_r1_polyAla.pdb', 'c1_t27_r3_polyAla.pdb', 'c1_t13_r1_polyAla.pdb',
            'c2_t95_r3_polyAla.pdb', 'c2_t81_r3_polyAla.pdb', 'c2_t66_r1_polyAla.pdb', 'c2_t56_r3_polyAla.pdb',
            'c2_t42_r1_polyAla.pdb', 'c2_t32_r3_polyAla.pdb', 'c2_t18_r1_polyAla.pdb', 'c2_t8_r3_polyAla.pdb',
            'c3_t81_r3_polyAla.pdb', 'c3_t56_r1_polyAla.pdb', 'c3_t42_r1_polyAla.pdb', 'c3_t32_r3_polyAla.pdb'
        ]
        ensemble_data = [
            {'truncation_score_key': None, 'truncation_level': 100, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 85, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 76, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 61, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 52, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 37, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 27, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 13, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 95, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 81, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 66, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 56, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 42, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 32, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 18, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 8, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 81, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 3},
            {'truncation_score_key': None, 'truncation_level': 56, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 3},
            {'truncation_score_key': None, 'truncation_level': 42, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 3},
            {'truncation_score_key': None, 'truncation_level': 32, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 3}
        ]
        out_order = [
            'c1_t13_r1_polyAla.pdb', 'c1_t27_r3_polyAla.pdb', 'c1_t37_r1_polyAla.pdb', 'c1_t52_r3_polyAla.pdb',
            'c1_t61_r1_polyAla.pdb', 'c1_t76_r3_polyAla.pdb', 'c1_t85_r1_polyAla.pdb', 'c1_t100_r3_polyAla.pdb',
            'c2_t8_r3_polyAla.pdb', 'c2_t18_r1_polyAla.pdb', 'c2_t32_r3_polyAla.pdb', 'c2_t42_r1_polyAla.pdb',
            'c2_t56_r3_polyAla.pdb', 'c2_t66_r1_polyAla.pdb', 'c2_t81_r3_polyAla.pdb', 'c2_t95_r3_polyAla.pdb',
            'c3_t32_r3_polyAla.pdb', 'c3_t42_r1_polyAla.pdb', 'c3_t56_r1_polyAla.pdb', 'c3_t81_r3_polyAla.pdb'
        ]
        sort_keys = ['cluster_num', 'truncation_level', 'subcluster_radius_threshold', 'side_chain_treatment']
        sorted_ensemble_pdbs = ensembler._sort_ensembles(ensemble_pdbs, ensemble_data, sort_keys, False)
        self.assertEqual(out_order, sorted_ensemble_pdbs)

    def test__sort_ensembles_2(self):
        ensemble_pdbs = [
            'c1_t100_r3_polyAla.pdb', 'c1_t85_r1_polyAla.pdb', 'c1_t76_r3_polyAla.pdb', 'c1_t61_r1_polyAla.pdb',
            'c1_t52_r3_polyAla.pdb', 'c1_t37_r1_polyAla.pdb', 'c1_t27_r3_polyAla.pdb', 'c1_t13_r1_polyAla.pdb',
            'c2_t95_r3_polyAla.pdb', 'c2_t81_r3_polyAla.pdb', 'c2_t66_r1_polyAla.pdb', 'c2_t56_r3_polyAla.pdb',
            'c2_t42_r1_polyAla.pdb', 'c2_t32_r3_polyAla.pdb', 'c2_t18_r1_polyAla.pdb', 'c2_t8_r3_polyAla.pdb',
            'c3_t81_r3_polyAla.pdb', 'c3_t56_r1_polyAla.pdb', 'c3_t42_r1_polyAla.pdb', 'c3_t32_r3_polyAla.pdb'
        ]
        ensemble_data = [
            {'truncation_score_key': None, 'truncation_level': 100, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 85, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 76, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 61, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 52, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 37, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 27, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 13, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 95, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 81, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 66, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 56, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 42, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 32, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 18, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 8, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 81, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 3},
            {'truncation_score_key': None, 'truncation_level': 56, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 3},
            {'truncation_score_key': None, 'truncation_level': 42, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 3},
            {'truncation_score_key': None, 'truncation_level': 32, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 3}
        ]
        out_order = [
            'c2_t8_r3_polyAla.pdb', 'c1_t13_r1_polyAla.pdb', 'c2_t18_r1_polyAla.pdb', 'c1_t27_r3_polyAla.pdb',
            'c2_t32_r3_polyAla.pdb', 'c3_t32_r3_polyAla.pdb', 'c1_t37_r1_polyAla.pdb', 'c2_t42_r1_polyAla.pdb',
            'c3_t42_r1_polyAla.pdb', 'c1_t52_r3_polyAla.pdb', 'c3_t56_r1_polyAla.pdb', 'c2_t56_r3_polyAla.pdb',
            'c1_t61_r1_polyAla.pdb', 'c2_t66_r1_polyAla.pdb', 'c1_t76_r3_polyAla.pdb', 'c2_t81_r3_polyAla.pdb',
            'c3_t81_r3_polyAla.pdb', 'c1_t85_r1_polyAla.pdb', 'c2_t95_r3_polyAla.pdb', 'c1_t100_r3_polyAla.pdb',
        ]
        sort_keys = ['truncation_level', 'subcluster_radius_threshold', 'side_chain_treatment', 'cluster_num']
        sorted_ensemble_pdbs = ensembler._sort_ensembles(ensemble_pdbs, ensemble_data, sort_keys, False)
        self.assertEqual(out_order, sorted_ensemble_pdbs)

    def test__sort_ensembles_3(self):
        ensemble_pdbs = [
            'c1_t100_r3_polyAla.pdb', 'c1_t85_r1_polyAla.pdb', 'c1_t76_r3_polyAla.pdb', 'c1_t61_r1_polyAla.pdb',
            'c1_t52_r3_polyAla.pdb', 'c1_t37_r1_polyAla.pdb', 'c1_t27_r3_polyAla.pdb', 'c1_t13_r1_polyAla.pdb',
            'c2_t95_r3_polyAla.pdb', 'c2_t81_r3_polyAla.pdb', 'c2_t66_r1_polyAla.pdb', 'c2_t56_r3_polyAla.pdb',
            'c2_t42_r1_polyAla.pdb', 'c2_t32_r3_polyAla.pdb', 'c2_t18_r1_polyAla.pdb', 'c2_t8_r3_polyAla.pdb',
            'c3_t81_r3_polyAla.pdb', 'c3_t56_r1_polyAla.pdb', 'c3_t42_r1_polyAla.pdb', 'c3_t32_r3_polyAla.pdb'
        ]
        ensemble_data = [
            {'truncation_score_key': None, 'truncation_level': 100, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 85, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 76, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 61, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 52, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 37, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 27, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 13, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 95, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 81, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 66, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 56, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 42, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 32, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 18, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 8, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 81, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 3},
            {'truncation_score_key': None, 'truncation_level': 56, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 3},
            {'truncation_score_key': None, 'truncation_level': 42, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 3},
            {'truncation_score_key': None, 'truncation_level': 32, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 3}
        ]
        out_order = [
            'c1_t27_r3_polyAla.pdb', 'c2_t32_r3_polyAla.pdb', 'c3_t32_r3_polyAla.pdb', 'c1_t37_r1_polyAla.pdb',
            'c2_t42_r1_polyAla.pdb', 'c3_t42_r1_polyAla.pdb', 'c2_t8_r3_polyAla.pdb', 'c1_t13_r1_polyAla.pdb',
            'c2_t18_r1_polyAla.pdb', 'c1_t52_r3_polyAla.pdb', 'c3_t56_r1_polyAla.pdb', 'c2_t56_r3_polyAla.pdb',
            'c1_t61_r1_polyAla.pdb', 'c2_t66_r1_polyAla.pdb', 'c1_t76_r3_polyAla.pdb', 'c2_t81_r3_polyAla.pdb',
            'c3_t81_r3_polyAla.pdb', 'c1_t85_r1_polyAla.pdb', 'c2_t95_r3_polyAla.pdb', 'c1_t100_r3_polyAla.pdb',
        ]
        sort_keys = ['truncation_level', 'subcluster_radius_threshold', 'side_chain_treatment', 'cluster_num']
        sorted_ensemble_pdbs = ensembler._sort_ensembles(ensemble_pdbs, ensemble_data, sort_keys, True)
        self.assertEqual(out_order, sorted_ensemble_pdbs)

    def test__sort_ensembles_4(self):
        ensemble_pdbs = [
            'c1_t100_r3_polyAla.pdb', 'c1_t85_r1_polyAla.pdb', 'c1_t76_r3_polyAla.pdb', 'c1_t61_r1_polyAla.pdb',
            'c1_t52_r3_polyAla.pdb', 'c1_t37_r1_polyAla.pdb', 'c1_t27_r3_polyAla.pdb', 'c1_t13_r1_polyAla.pdb',
            'c2_t95_r3_polyAla.pdb', 'c2_t81_r3_polyAla.pdb', 'c2_t66_r1_polyAla.pdb', 'c2_t56_r3_polyAla.pdb',
            'c2_t42_r1_polyAla.pdb', 'c2_t32_r3_polyAla.pdb', 'c2_t18_r1_polyAla.pdb', 'c2_t8_r3_polyAla.pdb',
            'c3_t81_r3_polyAla.pdb', 'c3_t56_r1_polyAla.pdb', 'c3_t42_r1_polyAla.pdb', 'c3_t32_r3_polyAla.pdb'
        ]
        ensemble_data = [
            {'truncation_score_key': None, 'truncation_level': 100, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 85, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 76, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 61, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 52, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 37, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 27, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 13, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 1},
            {'truncation_score_key': None, 'truncation_level': 95, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 81, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 66, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 56, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 42, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 32, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 18, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 8, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 2},
            {'truncation_score_key': None, 'truncation_level': 81, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 3},
            {'truncation_score_key': None, 'truncation_level': 56, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 3},
            {'truncation_score_key': None, 'truncation_level': 42, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 1, 'cluster_num': 3},
            {'truncation_score_key': None, 'truncation_level': 32, 'side_chain_treatment': 'polyAla',
             'subcluster_radius_threshold': 3, 'cluster_num': 3}
        ]
        out_order = [
            'c1_t27_r3_polyAla.pdb', 'c1_t37_r1_polyAla.pdb', 'c1_t13_r1_polyAla.pdb', 'c1_t52_r3_polyAla.pdb',
            'c1_t61_r1_polyAla.pdb', 'c1_t76_r3_polyAla.pdb', 'c1_t85_r1_polyAla.pdb', 'c1_t100_r3_polyAla.pdb',
            'c2_t32_r3_polyAla.pdb', 'c2_t42_r1_polyAla.pdb', 'c2_t8_r3_polyAla.pdb', 'c2_t18_r1_polyAla.pdb',
            'c2_t56_r3_polyAla.pdb', 'c2_t66_r1_polyAla.pdb', 'c2_t81_r3_polyAla.pdb', 'c2_t95_r3_polyAla.pdb',
            'c3_t32_r3_polyAla.pdb', 'c3_t42_r1_polyAla.pdb', 'c3_t56_r1_polyAla.pdb', 'c3_t81_r3_polyAla.pdb'
        ]
        sort_keys = ['cluster_num', 'truncation_level', 'subcluster_radius_threshold', 'side_chain_treatment']
        sorted_ensemble_pdbs = ensembler._sort_ensembles(ensemble_pdbs, ensemble_data, sort_keys, True)
        self.assertEqual(out_order, sorted_ensemble_pdbs)

    def test__sort_ensembles_5(self):
        ensemble_pdbs = [
            'concoord_t100_polyAla.pdb', 'concoord_t100_reliable.pdb', 'concoord_t100_allatom.pdb',
            'concoord_t80_polyAla.pdb', 'concoord_t80_reliable.pdb', 'concoord_t80_allatom.pdb',
            'concoord_t60_polyAla.pdb', 'concoord_t60_reliable.pdb', 'concoord_t60_allatom.pdb',
            'concoord_t40_polyAla.pdb', 'concoord_t40_reliable.pdb', 'concoord_t40_allatom.pdb',
            'concoord_t20_polyAla.pdb', 'concoord_t20_reliable.pdb', 'concoord_t20_allatom.pdb'
        ]
        ensemble_data = [
            {'truncation_level': 100, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'polyAla'},
            {'truncation_level': 100, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'reliable'},
            {'truncation_level': 100, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'allatom'},
            {'truncation_level': 80, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'polyAla'},
            {'truncation_level': 80, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'reliable'},
            {'truncation_level': 80, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'allatom'},
            {'truncation_level': 60, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'polyAla'},
            {'truncation_level': 60, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'reliable'},
            {'truncation_level': 60, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'allatom'},
            {'truncation_level': 40, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'polyAla'},
            {'truncation_level': 40, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'reliable'},
            {'truncation_level': 40, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'allatom'},
            {'truncation_level': 20, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'polyAla'},
            {'truncation_level': 20, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'reliable'},
            {'truncation_level': 20, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'allatom'}
        ]
        out_order = [
            'concoord_t20_allatom.pdb', 'concoord_t40_allatom.pdb', 'concoord_t60_allatom.pdb',
            'concoord_t80_allatom.pdb', 'concoord_t100_allatom.pdb', 'concoord_t20_polyAla.pdb',
            'concoord_t40_polyAla.pdb', 'concoord_t60_polyAla.pdb', 'concoord_t80_polyAla.pdb',
            'concoord_t100_polyAla.pdb', 'concoord_t20_reliable.pdb', 'concoord_t40_reliable.pdb',
            'concoord_t60_reliable.pdb', 'concoord_t80_reliable.pdb', 'concoord_t100_reliable.pdb'
        ]
        sort_keys = ['side_chain_treatment', 'truncation_score_key', 'truncation_level']
        sorted_ensemble_pdbs = ensembler._sort_ensembles(ensemble_pdbs, ensemble_data, sort_keys, False)
        self.assertEqual(out_order, sorted_ensemble_pdbs)

    def test__sort_ensembles_6(self):
        ensemble_pdbs = [
            'concoord_t100_polyAla.pdb', 'concoord_t100_reliable.pdb', 'concoord_t100_allatom.pdb',
            'concoord_t80_polyAla.pdb', 'concoord_t80_reliable.pdb', 'concoord_t80_allatom.pdb',
            'concoord_t60_polyAla.pdb', 'concoord_t60_reliable.pdb', 'concoord_t60_allatom.pdb',
            'concoord_t40_polyAla.pdb', 'concoord_t40_reliable.pdb', 'concoord_t40_allatom.pdb',
            'concoord_t20_polyAla.pdb', 'concoord_t20_reliable.pdb', 'concoord_t20_allatom.pdb'
        ]
        ensemble_data = [
            {'truncation_level': 100, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'polyAla'},
            {'truncation_level': 100, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'reliable'},
            {'truncation_level': 100, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'allatom'},
            {'truncation_level': 80, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'polyAla'},
            {'truncation_level': 80, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'reliable'},
            {'truncation_level': 80, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'allatom'},
            {'truncation_level': 60, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'polyAla'},
            {'truncation_level': 60, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'reliable'},
            {'truncation_level': 60, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'allatom'},
            {'truncation_level': 40, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'polyAla'},
            {'truncation_level': 40, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'reliable'},
            {'truncation_level': 40, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'allatom'},
            {'truncation_level': 20, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'polyAla'},
            {'truncation_level': 20, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'reliable'},
            {'truncation_level': 20, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'allatom'}
        ]
        out_order = [
            'concoord_t20_allatom.pdb', 'concoord_t20_polyAla.pdb', 'concoord_t20_reliable.pdb',
            'concoord_t40_allatom.pdb', 'concoord_t40_polyAla.pdb', 'concoord_t40_reliable.pdb',
            'concoord_t60_allatom.pdb', 'concoord_t60_polyAla.pdb', 'concoord_t60_reliable.pdb',
            'concoord_t80_allatom.pdb', 'concoord_t80_polyAla.pdb', 'concoord_t80_reliable.pdb',
            'concoord_t100_allatom.pdb', 'concoord_t100_polyAla.pdb', 'concoord_t100_reliable.pdb'
        ]
        sort_keys = ['truncation_level', 'side_chain_treatment', 'truncation_score_key']
        sorted_ensemble_pdbs = ensembler._sort_ensembles(ensemble_pdbs, ensemble_data, sort_keys, True)
        self.assertEqual(out_order, sorted_ensemble_pdbs)

    def test__sort_ensembles_7(self):
        ensemble_pdbs = [
            'concoord_t100_polyAla.pdb', 'concoord_t100_reliable.pdb', 'concoord_t100_allatom.pdb',
            'apple_t80_polyAla.pdb', 'concoord_t80_reliable.pdb', 'concoord_t80_allatom.pdb',
            'concoord_t60_polyAla.pdb', 'concoord_t60_reliable.pdb', 'apple_t60_allatom.pdb',
            'concoord_t40_polyAla.pdb', 'concoord_t40_reliable.pdb', 'concoord_t40_allatom.pdb',
            'concoord_t20_polyAla.pdb', 'tree_t20_reliable.pdb', 'concoord_t20_allatom.pdb'
        ]
        ensemble_data = [
            {'truncation_level': 100, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'polyAla'},
            {'truncation_level': 100, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'reliable'},
            {'truncation_level': 100, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'allatom'},
            {'truncation_level': 80, 'truncation_score_key': 'apple', 'side_chain_treatment': 'polyAla'},
            {'truncation_level': 80, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'reliable'},
            {'truncation_level': 80, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'allatom'},
            {'truncation_level': 60, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'polyAla'},
            {'truncation_level': 60, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'reliable'},
            {'truncation_level': 60, 'truncation_score_key': 'apple', 'side_chain_treatment': 'allatom'},
            {'truncation_level': 40, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'polyAla'},
            {'truncation_level': 40, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'reliable'},
            {'truncation_level': 40, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'allatom'},
            {'truncation_level': 20, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'polyAla'},
            {'truncation_level': 20, 'truncation_score_key': 'tree', 'side_chain_treatment': 'reliable'},
            {'truncation_level': 20, 'truncation_score_key': 'concoord', 'side_chain_treatment': 'allatom'}
        ]
        out_order = [
            'apple_t60_allatom.pdb', 'apple_t80_polyAla.pdb', 'concoord_t20_allatom.pdb',
            'concoord_t20_polyAla.pdb', 'concoord_t40_allatom.pdb', 'concoord_t40_polyAla.pdb',
            'concoord_t40_reliable.pdb', 'concoord_t60_polyAla.pdb', 'concoord_t60_reliable.pdb',
            'concoord_t80_allatom.pdb', 'concoord_t80_reliable.pdb',  'concoord_t100_allatom.pdb',
            'concoord_t100_polyAla.pdb', 'concoord_t100_reliable.pdb', 'tree_t20_reliable.pdb'
        ]
        sort_keys = ['truncation_score_key', 'truncation_level', 'side_chain_treatment']
        sorted_ensemble_pdbs = ensembler._sort_ensembles(ensemble_pdbs, ensemble_data, sort_keys, True)
        self.assertEqual(out_order, sorted_ensemble_pdbs)

if __name__ == "__main__":
    unittest.main(verbosity=2)