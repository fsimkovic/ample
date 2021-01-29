"""
30.01.2016

@author: hlfsimko
"""
import logging
import multiprocessing
import os
import sys
import traceback

from ample.constants import AMPLE_CONFIG_FILE
from ample.ensembler.constants import POLYALA, RELIABLE, ALLATOM, SPICKER_TM
from ample.util import version

try:
    from configparser import ConfigParser as SafeConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser

logger = logging.getLogger(__name__)

##############################################################
# The sections and options within need to be stored
# otherwise we cannot manage interplay between
# ConfigParser and AMPLE settings dictionary.
# Some default non-dynamic parts are stored below to avoid errors
_SECTIONS_REFERENCE = {
    "AMPLE_info": ["ample_version", "ccp4_version", "cmdline_flags"],
    "Databases": ['nr', 'rosetta_db'],
    "Ensembling": [],
    "Executables": [
        'blast_dir',
        'cluster_exe',
        'fast_protein_cluster_exe',
        'gesamt_exe',
        'mustang_exe',
        'rosetta_dir',
        'rosetta_fragments_exe',
        'rosetta_executable',
        'scwrl_exe',
        'shelxe_exe',
        'spicker_exe',
        'theseus_exe',
    ],
    "Files": [
        'alignment_file',
        'ample_log',
        'bbcontacts_file',
        'cluster_dir',
        'config_file',
        'contact_file',
        'disulfide_constraints_file',
        'ensembles',
        'ensembles_directory',
        'ensemble_ok',
        'existing_mr_solution',
        'fasta',
        'frags_3mers',
        'frags_9mers',
        'models',
        'models_dir',
        'mrbump_dir',
        'mr_sequence',
        'mtz',
        'native_pdb',
        'native_mtz',
        'nmr_model_in',
        'nmr_remodel_fasta',
        'out_config_file',
        'psipred_ss2',
        'restart_pkl',
        'restraints_file',
        'results_path',
        'score_matrix',
        'score_matrix_file_list',
        'sf_cif',
        'single_model',
        'transmembrane_octopusfile',
        'transmembrane_lipofile',
        'transmembrane_spanfile',
        'truncation_scorefile',
        'work_dir',
    ],
    "General": [],
    "Modelling": [],
    "Restraints": [],
    # Data stored in amopt.d but not really part of AMPLE's configuration
    "No_config": [
        "benchmark_results",
        "ensembles_data",
        "fasta_length",
        "mrbump_results",
        "sequence",
        "truncation_variances",
        "truncation_levels",
        "truncation_nresidues",
    ],
    # In case we haven't specified anything or it is new
    "Unspecified": [],
}


class DebugDict(dict):
    """A Dictionary class that prints when watched items are set or accessed"""

    def __init__(self, *args, **kwargs):
        dict.__init__(self, args)
        self.watchkeys = []
        if 'watchkeys' in kwargs:
            watchkeys = kwargs['watchkeys']
            if not isinstance(watchkeys, list):
                list(watchkeys)
            self.watchkeys = watchkeys

    def __getitem__(self, key):
        val = dict.__getitem__(self, key)
        if key in self.watchkeys:
            logger.info("AMOPT GET {0}['{1}'] = {2}".format(dict.get(self, 'name_label'), key, val))
            logger.info(
                "AMOPT STACK:\n{0}".format(os.linesep.join(traceback.format_list(traceback.extract_stack())[:-1]))
            )
        return val

    def __setitem__(self, key, val):
        if key in self.watchkeys:
            logger.info("AMOPT SET {0}['{1}'] = {2}".format(dict.get(self, 'name_label'), key, val))
            logger.info(
                "AMOPT STACK:\n{0}".format(os.linesep.join(traceback.format_list(traceback.extract_stack())[:-1]))
            )
        dict.__setitem__(self, key, val)


class AMPLEConfigOptions(object):
    def __init__(self):

        self.d = {}  # Can't use defaultdict as need lambda function to return None, which won't pickle
        # self.d = DebugDict(watchkeys=['models'])
        self.cmdline_opts = {}
        self.debug = False

        # The original AMPLE clustering/truncation mode used in all work prior to January 2017
        self.classic_mode = {
            'percent': 5,
            'num_clusters': 1,
            'subcluster_radius_thresholds': [1, 2, 3],
            'side_chain_treatments': [POLYALA, RELIABLE, ALLATOM],
        }

        # Test use scrwl
        self.devel_mode = {
            'benchmark_mode': True,
            'early_terminate': False,
            'shelxe_rebuild': True,
            'shelxe_rebuild_arpwarp': True,
            'shelxe_rebuild_buccaneer': True,
            'refine_rebuild_arpwarp': False,
            'refine_rebuild_buccaneer': False,
            #'mr_keys' : [ [ 'PKEY', 'KILL','TIME','360'  ] ],
        }

        self.quick_mode = {
            'ensemble_max_models': 10,
            'nmodels': 200,
            'percent': 20,
            'shelx_cycles': 5,
            'refine_rebuild_arpwarp': False,
            'refine_rebuild_buccaneer': False,
            'phaser_kill': 15,
        }

        self.webserver_uri = {
            'shelxe_rebuild_arpwarp': False,  # Need to sort out the ArpWarp licence details
            'shelxe_rebuild_buccaneer': True,
            'cluster_method': SPICKER_TM,
            'nproc': 1,
            'purge': 1,
            'submit_cluster': True,
            'submit_max_array': 10,
            'submit_qtype': "SGE",
            'submit_queue': "all.q",
        }

    def populate(self, cmdline_opts):
        self.cmdline_opts = cmdline_opts

        # Identify which config file to use
        config_file = self._get_config_file(cmdline_opts['config_file'])

        # Read the configuration file
        self._read_config_file(config_file)

        # Read the command line arguments
        self._read_cmdline_opts(cmdline_opts)

        # Set further options
        self._process_options()
        return

    def _get_config_file(self, cmd_file=None):
        config_file = os.path.abspath(cmd_file) if cmd_file else AMPLE_CONFIG_FILE
        if not os.path.isfile(config_file):
            msg = "Cannot find configuration file: {0} - terminating...".format(config_file)
            logger.critical(msg)
            raise RuntimeError(msg)
        logger.debug("Using configuration file: {0}".format(config_file))
        return config_file

    def _process_options(self):
        """
        Handle any top-level options that affect the overall running of AMPLE.

        Notes
        -----
        Any specific processing of options should be handled in ample/util/options_processor.py/process_options

        See Also
        --------
        options_processor

        """
        self.d['ample_version'] = version.__version__
        if "rcdir" in self.d and not self.d["rcdir"]:
            self.d["rcdir"] = os.path.join(os.path.expanduser("~"), ".ample")
        # Set full file paths
        if sys.version_info.major == 3:
            d_items = self.d.items()
        else:
            d_items = self.d.iteritems()
        for k, v in d_items:
            if k in _SECTIONS_REFERENCE["Files"] and v:
                self.d[k] = os.path.abspath(v)

        # Use the maximum number of processors unless overridden by the user
        if self.d['nproc'] is None:
            if self.d['submit_cluster']:
                self.d['nproc'] = 1
            else:
                self.d['nproc'] = multiprocessing.cpu_count()

        # Check if using any preset options
        if self.d['classic_mode']:
            self._preset_options('classic_mode')
        if self.d['devel_mode']:
            self._preset_options('devel_mode')
        if self.d['quick_mode']:
            self._preset_options('quick_mode')
        if self.d['thin_clusters']:
            self._preset_options('thin_clusters')
        if self.d['webserver_uri']:
            self._preset_options('webserver_uri')
        return

    def _preset_options(self, mode):
        assert hasattr(self, mode), "Unknown mode: {0}".format(mode)
        logger.info("Using preset mode: {0}".format(mode))
        if sys.version_info.major == 3:
            d_items = getattr(self, mode).items()
        else:
            d_items = getattr(self, mode).iteritems()
        for k, v in d_items:
            if 'cmdline_flags' in self.d and k in self.d['cmdline_flags']:
                if self.d[k] == v:
                    msg = 'WARNING! {0} flag {1} => {2} was duplicated on the command line!'.format(mode, v, k)
                else:
                    msg = "WARNING! Overriding {0} setting: {1} => {2} with {3}".format(mode, k, v, self.d[k])
                logger.critical(msg)
            elif k in self.d:
                logger.debug("{0} overriding default setting: {1} => {2} with {3}".format(mode, k, v, self.d[k]))
                self.d[k] = v
            else:
                logger.debug("{0} setting: {1} => {2}".format(mode, k, v))
                self.d[k] = v
        return

    def _read_config_file(self, config_file):
        config = SafeConfigParser()
        # We need to make sure that the keys aren't converted to lower case on reading
        config.optionxform = str
        config.read(config_file)
        for section in config.sections():
            if not section in _SECTIONS_REFERENCE:
                _SECTIONS_REFERENCE[section] = []
            # Basic switch statement to determine the type of the variable
            for k, v in config.items(section):
                if v.lower() == "none":
                    self.d[k] = None

                elif v.lower() == "true":
                    self.d[k] = True

                elif v.lower() == "false":
                    self.d[k] = False

                elif section.lower() == "databases":
                    self.d[k] = os.path.abspath(v)

                elif section.lower() == "executables":
                    self.d[k] = os.path.abspath(v)

                elif section.lower() == "files":
                    self.d[k] = os.path.abspath(v)

                elif v.isdigit():
                    self.d[k] = int(v)

                elif self._isfloat(v):
                    self.d[k] = float(v)

                else:
                    self.d[k] = v

                _SECTIONS_REFERENCE[section].append(k)
        return

    def _read_cmdline_opts(self, cmdline_opts):
        tmpv = None
        cmdline_flags = []
        if sys.version_info.major == 3:
            d_items = cmdline_opts.items()
        else:
            d_items = cmdline_opts.iteritems()
        for k, v in d_items:
            if v is not None:
                cmdline_flags.append(k)
            if k not in self.d:
                self.d[k] = v
            elif v != None:
                logger.debug("Cmdline changing {0}: {1} => {2}".format(k, self.d[k], v))
                self.d[k] = v
        self.d['cmdline_flags'] = sorted(cmdline_flags)
        return

    def _isfloat(self, value):
        try:
            float(value)
            return True
        except:
            return False

    def prettify_parameters(self):
        """Return the parameters nicely formated as a list of strings suitable
        for writing out to a file"""
        pstr = 'Parameters Used in this Run\n\n'
        for k, v in sorted(self.d.items()):
            pstr += "{0} : {1}\n".format(k, v)
        return pstr

    def write_config_file(self, config_file=None):
        config = SafeConfigParser()
        # We need to make sure that the keys aren't converted to lower case on writing
        config.optionxform = str
        self._update_config(config)
        if config_file is None:
            # Can be None for testing
            config_file = os.path.join(self.d['work_dir'], self.d['name'] + ".ini")
        # Write config to job specific directory
        self.d["out_config_file"] = config_file
        logger.info("AMPLE configuration written to: {0}".format(config_file))
        with open(config_file, "w") as out:
            config.write(out)
        return

    def _update_config(self, config_parser):
        # Add all sections to the configparser
        for section in sorted(_SECTIONS_REFERENCE.keys()):
            if section.lower() == "no_config":
                continue
            config_parser.add_section(section)

        # Place all entries in our dictionary in the corresponding section in
        # the configparser
        for option in sorted(self.d.keys()):
            # Extract the section in which the entry needs to go
            sections = [
                k for (k, v) in _SECTIONS_REFERENCE.items() if any(entry.lower() == option.lower() for entry in v)
            ]

            # Make sure we only have each option assigned to a single section
            section = "Unspecified" if len(sections) != 1 else sections[0]

            # We do not want to re-use files or at least not by default.
            # Comment those specifically out to avoid any errors
            if section.lower() == "no_config":
                continue
            elif section.lower() == "ample_info" or section.lower() == "files" or section.lower() == "unspecified":
                config_parser.set(section, "#" + option, str(self.d[option]))
            else:
                config_parser.set(section, option, str(self.d[option]))
        return
