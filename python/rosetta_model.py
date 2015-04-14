'''
Created on 21 Feb 2013

@author: jmht
'''

# Python modules
import glob
import logging
import os
import random
import re
import shutil
import unittest

# Our modules
import add_sidechains_SCWRL
import ample_sequence
import ample_util
import clusterize
import octopus_predict
import pdb_edit
import workers

def align_mafft(query_seq, template_seq, logger, mafft_exe=None):
    if not mafft_exe:
        mafft_exe = os.path.join(os.environ['CCP4'], 'libexec', 'mafft')
        if not ample_util.is_exe(mafft_exe): raise RuntimeError,"Cannot find CCP4 mafft binary: {0}".format(mafft_exe)
        
    name = "{0}__{1}".format(query_seq.name,template_seq.name)
    mafft_input = "{0}_concat.fasta".format(name)
    query_seq.concat(template_seq,mafft_input)
    cmd =  [mafft_exe, '--maxiterate', '1000', '--localpair', '--quiet', mafft_input]
    logfile = os.path.abspath('mafft.out')
    
    ret = ample_util.run_command(cmd,logfile=logfile)
    if ret != 0:
        raise RuntimeError,"Error running mafft for alignnment - check logfile: {0}".format(logfile)
    
    seq_align = ample_sequence.Sequence()
    seq_align.from_fasta(logfile,canonicalise=False)
    
    logger.info("Got Alignment:\n{0}\n{1}".format(seq_align.sequences[0],seq_align.sequences[1]))
    logger.info("If you want to use a different alignment, import using -alignment_file")
    
    alignment_file = "{0}_align.grishin".format(name)
    with open(alignment_file,'w') as w:
        # First line is query and template name - must match the name of the template pdb
        w.write("""## {0}  {1}
# hhsearch\n
scores_from_program: 0 1.00\n'+
0 {2}
0 {3}
""".format(query_seq.name,template_seq.name,seq_align.sequences[0], seq_align.sequences[1]))
    return os.path.abspath(alignment_file)

def align_clustalw(query_seq, template_seq, logger, clustalw_exe=None):
    if not clustalw_exe:
        mafft_exe = os.path.join(os.environ['CCP4'], 'libexec', 'clustalw2')
        if not ample_util.is_exe(mafft_exe): raise RuntimeError,"Cannot find CCP4 clustalw2 binary: {0}".format(mafft_exe)
        
    name = "{0}__{1}".format(query_seq.name,template_seq.name)
    clustalw_input = "{0}_concat.fasta".format(name)
    query_seq.concat(template_seq,clustalw_input)
    align_out="{0}_align.fasta".format(name)
    logfile=os.path.abspath("clustalw2.log")
    cmd =  [clustalw_exe,
            '-align',
            '-outorder=input',
            '-output=fasta',
            '-infile={0}'.format(clustalw_input),
            '-outfile={0}'.format(align_out)]
    
    ret = ample_util.run_command(cmd,logfile=logfile)
    if ret != 0:
        raise RuntimeError,"Error running clustalw2 for alignnment - check logfile: {0}".format(logfile)
    
    seq_align = ample_sequence.Sequence()
    seq_align.from_fasta(align_out,canonicalise=False)
    
    logger.info("Got Alignment:\n{0}\n{1}".format(seq_align.sequences[0],seq_align.sequences[1]))
    logger.info("If you want to use a different alignment, import using -alignment_file")
    
    alignment_file = "{0}_align.grishin".format(name)
    with open(alignment_file,'w') as w:
        # First line is query and template name - must match the name of the template pdb
        w.write("""## {0}  {1}
# hhsearch\n
scores_from_program: 0 1.00\n'+
0 {2}
0 {3}
""".format(query_seq.name,template_seq.name,seq_align.sequences[0], seq_align.sequences[1]))
    return os.path.abspath(alignment_file)

class RosettaModel(object):
    """
    Class to run Rosetta modelling
    """

    def __init__(self,optd=None,rosetta_dir=None):

        self.debug=None

        self.nproc = None
        self.nmodels = None
        self.work_dir = None
        self.models_dir = None
        self.rosetta_dir = None
        self.rosetta_bin = None
        self.rosetta_AbinitioRelax = None
        self.rosetta_cluster = None
        self.rosetta_mr_protocols = None
        self.rosetta_idealize_jd2 = None
        self.rosetta_db = None
        self.rosetta_version = None

        # Not used yet
        self.make_models = None
        self.make_fragments = None

        self.fasta = None
        self.all_atom = None
        self.use_scwrl = None
        self.scwrl_exe = None

        # Fragment variables
        self.name = None
        self.frags_3mers = None
        self.frags_9mers = None
        self.use_homs = None
        self.fragments_directory = None
        self.fragments_exe = None

        # Transmembrane variables
        self.transmembrane = None
        self.octopus2span = None
        self.run_lips = None
        self.align_blast = None
        self.nr = None
        self.blastpgp = None
        self.octopusTopology = None
        self.spanfile = None
        self.lipofile = None

        # List of seeds
        self.seeds = None

        # Extra options
        self.psipred_ss2 = None
        self.domain_termini_distance = None
        self.rad_gyr_reweight = None
        self.improve_template = None
        self.nativePdbStd = None
        self.constraints_file = None

        self.logger = logging.getLogger()

        self.set_paths(optd=optd, rosetta_dir=rosetta_dir)
        if optd:
            self.set_from_dict(optd)
        return

    def ab_initio_model(self,monitor):
        
        # Add submit_cluster, submit_queue, submit_qtype
        if not os.path.isdir(self.models_dir): os.mkdir(self.models_dir)
        if self.transmembrane: self.generate_tm_predict()    
    
        # Split jobs onto separate processors - 1 for cluster, as many as will fit for desktop
        if self.submit_cluster:
            jobs_per_proc=[1] * self.nmodels
        else:
            jobs_per_proc=self.split_jobs(self.nmodels,self.nproc)
        
        # Generate seeds
        seeds = self.generate_seeds(len(jobs_per_proc))
        
        # Make the directories and put the run scripts in them
        run_dir = os.path.join(self.work_dir, 'modelling')
        os.mkdir(run_dir)
        os.chdir(run_dir)
        job_scripts=[]
        dir_list = []
        job_time=7200
        for i, njobs in enumerate(jobs_per_proc):
            d=os.path.join(run_dir,"job_{0}".format(i))
            os.mkdir(d)
            dir_list.append(d)
            
            # job script
            script="#!/bin/bash\n"
            if self.submit_cluster:
                script += clusterize.ClusterRun().queueDirectives(nProc=1,
                                                                  jobTime=job_time,
                                                                  queue=self.submit_queue,
                                                                  qtype=self.submit_qtype)
            
            cmd = " ".join(self.modelling_cmd(d, njobs, seeds[i]))
            script += cmd + "\n"
    
            sname=os.path.join(d,"model_{0}.sh".format(i))
            with open(sname,'w') as w: w.write(script)
            os.chmod(sname, 0o777)
            job_scripts.append(sname)
            
        success = self.run_scripts(job_scripts, job_time=job_time, monitor=None)
        if not success:
            raise RuntimeError, "Error running ROSETTA in directory: {0}\nPlease check the log files for more information.".format(run_dir)
        # Copy the models into the models directory - need to rename them accordingly
        pdbs = []
        for d in dir_list:
            ps = glob.glob(os.path.join(d, "*.pdb"))
            pdbs += ps
        
        if not len(pdbs):
            raise RuntimeError, "No pdbs after modelling in directory: {0}\nPlease check the log files for more information.".format(run_dir)
        
        if self.use_scwrl: scwrl = add_sidechains_SCWRL.Scwrl(scwrlExe=self.scwrl_exe)
        for i, pdbin in enumerate(pdbs):
            if self.use_scwrl:
                pdbout=os.path.join(self.models_dir,"model_{0}_scwrl.pdb".format(i))
                scwrl.addSidechains(pdbin=pdbin,pdbout=pdbout)
            else:
                pdbout=os.path.join(self.models_dir,"model_{0}.pdb".format(i))
                shutil.copyfile(pdbin, pdbout)   
        return

    def find_binary(self, name):
        """
        Find a rosetta binary on different platforms
        separate from object as it's currently used by the NMR stuff - which is in dire need of refactoring.

        """
        assert self.rosetta_bin and os.path.isdir(self.rosetta_bin)
        binaries = glob.glob( self.rosetta_bin + "/{0}.*".format( name )  )
        if not len( binaries ): return False

        # Could check for shortest - for now just return the first
        binary = os.path.abspath(binaries[0])
        if os.path.isfile(binary): return binary
        return False

    def generate_seeds(self, nseeds):
        """
        Generate a list of nseed seeds
        """
        start=1000000
        end=4000000
        assert nseeds > 0 and nseeds < end-start,"Invalid seed count: {0}".format(nseeds)
        seed_list = set()
        # Generate the list of random seeds
        while len(seed_list) < nseeds: seed_list.add(random.randint(start, end))
        # Keep a log of the seeds
        with open(os.path.join(self.work_dir,'seedlist'), "w") as seedlog:
            for seed in seed_list: seedlog.write(str(seed) + '\n')
        seed_list=list(seed_list)
        self.seeds = seed_list
        return seed_list

    def split_jobs(self,njobs,nproc):
        """
        Return a list of number of jobs to run on each processor
        """
        split_jobs = njobs / nproc  # split jobs between processors
        remainder = njobs % nproc
        jobs = []
        for i in range(nproc):
            njobs = split_jobs
            # Separate out remainder over jobs
            if remainder > 0:
                njobs += 1
                remainder -= 1
            jobs.append(njobs)
        return jobs

    def fragment_cmd(self):
        """
        Return the command to make the fragments as a list

        """
        # It seems that the script can't tolerate "-" in the directory name leading to the fasta file,
        # so we need to copy the fasta file into the fragments directory and just use the name here
        fasta = os.path.split(  self.fasta )[1]

        cmd = [ self.fragments_exe,
               '-rundir', self.fragments_directory,
               '-id', self.name,
                fasta ]

        if self.transmembrane:
            cmd += [ '-noporter', '-nopsipred','-sam']
        else:
            # version dependent flags
            if self.rosetta_version == 3.3:
                # jmht the last 3 don't seem to work with 3.4
                cmd += ['-noporter', '-nojufo', '-nosam','-noprof' ]
            elif self.rosetta_version >= 3.4:
                cmd += ['-noporter' ]

        # Whether to exclude homologs
        if not self.use_homs:
            cmd.append('-nohoms')

        # Be 'chatty'
        if self.debug:
            cmd.append('-verbose')

        return cmd

    def generate_fragments(self, amoptd):
        """
        Run the script to generate the fragments
        """
        self.logger.info('----- making fragments--------')
        if not os.path.exists( self.fragments_directory):
            os.mkdir( self.fragments_directory )

        # It seems that the script can't tolerate "-" in the directory name leading to the fasta file,
        # so we need to copy the fasta file into the fragments directory
        fasta = os.path.split(self.fasta)[1]
        shutil.copy2(self.fasta, self.fragments_directory + os.sep + fasta)

        cmd = self.fragment_cmd()
        logfile = os.path.join(self.fragments_directory, "make_fragments.log")

        if amoptd['submit_cluster']:
            submit_qtype=amoptd['submit_qtype']
            cluster_run = clusterize.ClusterRun()
            cluster_run.QTYPE=submit_qtype
            self.logger.info('Submitting fragment generation jobs to a queueing system of type: {0}\n'.format(submit_qtype))
            script_path = os.path.join(self.fragments_directory, "submit_fragments.sh" )
            cluster_run.writeFragmentsSubscript(cmd=" ".join(cmd),
                                                script_path=script_path,
                                                nProc=amoptd['nproc'],
                                                logFile=logfile,
                                                qtype=submit_qtype,
                                                queue=amoptd['submit_queue']
                                                )
            cluster_run.submitJob(subScript=script_path, jobDir=self.fragments_directory)
            cluster_run.monitorQueue() # Monitor the cluster queue to see when all jobs have finished
        else:
            retcode = ample_util.run_command(cmd, logfile=logfile, directory=self.fragments_directory)
            if retcode != 0:
                msg = "Error generating fragments!\nPlease check the logfile {0}".format( logfile )
                self.logger.critical( msg )
                raise RuntimeError, msg

        if self.rosetta_version >= 3.4:
            # new name format: $options{runid}.$options{n_frags}.$size" . "mers
            self.frags_3mers = self.fragments_directory + os.sep + self.name + '.200.3mers'
            self.frags_9mers = self.fragments_directory + os.sep + self.name + '.200.9mers'
        else:
            # old_name_format: aa$options{runid}$fragsize\_05.$options{n_frags}\_v1_3"
            self.frags_3mers = self.fragments_directory + os.sep + 'aa' + self.name + '03_05.200_v1_3'
            self.frags_9mers = self.fragments_directory + os.sep + 'aa' + self.name + '09_05.200_v1_3'

        if not os.path.exists( self.frags_3mers ) or not os.path.exists( self.frags_9mers ):
            raise RuntimeError, "Error making fragments - could not find fragment files:\n{0}\n{1}\n".format(self.frags_3mers,self.frags_9mers)

        self.logger.info('Fragments Done\n3mers at: ' + self.frags_3mers + '\n9mers at: ' + self.frags_9mers + '\n\n')

        if os.path.exists( self.fragments_directory + os.sep + self.fragments_directory + '.psipred'):
            ample_util.get_psipred_prediction( self.fragments_directory + os.sep + self.name + '.psipred')

        return
    ##End fragment_cmd

    def generate_tm_predict(self):
        """
        Generate the various files needed for modelling transmembrane proteins

        REM the fasta as it needs to reside in this directory or the script may fail
        due to problems with parsing directory names with 'funny' characters
        """

        # Files have already been created
        if os.path.isfile( str(self.spanfile) ) and os.path.isfile( str(self.lipofile) ):
            self.logger.debug("Using given span file: {0}\n and given lipo file: {1}".format( self.spanfile, self.lipofile ) )
            return

        # It seems that the script can't tolerate "-" in the directory name leading to the fasta file,
        # so we need to copy the fasta file into the fragments directory
        fasta = os.path.split(  self.fasta )[1]
        shutil.copy2( self.fasta, self.models_dir + os.sep + fasta )

        # See if we need to query the octopus server
        if os.path.isfile( str(self.octopusTopology) ):
            self.logger.info("Using user-supplied topology prediction file: {0}".format(self.octopusTopology))
        else:
            # Query octopus server for prediction
            octo = octopus_predict.OctopusPredict()
            self.logger.info("Generating predictions for transmembrane regions using octopus server: {0}".format(octo.octopus_url))
            #fastaseq = octo.getFasta(self.fasta)
            # Problem with 3LBW predicition when remove X
            fastaseq = octo.getFasta(self.fasta)
            octo.getPredict(self.name,fastaseq, directory=self.models_dir )
            self.octopusTopology = octo.topo
            self.logger.debug("Got topology prediction file: {0}".format(self.octopusTopology))

        # Generate span file from predict
        self.spanfile = os.path.join(self.models_dir, self.name + ".span")
        self.logger.debug( 'Generating span file {0}'.format( self.spanfile ) )
        cmd = [ self.octopus2span, self.octopusTopology ]
        retcode = ample_util.run_command( cmd, logfile=self.spanfile, directory=self.models_dir )
        if retcode != 0:
            msg = "Error generating span file. Please check the log in {0}".format(self.spanfile)
            self.logger.critical(msg)
            raise RuntimeError,msg

        # Now generate lips file
        self.logger.debug('Generating lips file from span')
        logfile = self.models_dir + os.sep + "run_lips.log"
        cmd = [ self.run_lips, fasta, self.spanfile, self.blastpgp, self.nr, self.align_blast ]
        retcode = ample_util.run_command( cmd, logfile=logfile, directory=self.models_dir )

        # Script only uses first 4 chars to name files
        lipofile = os.path.join(self.models_dir, self.name[0:4] + ".lips4")
        if retcode != 0 or not os.path.exists(lipofile):
            msg = "Error generating lips file {0}. Please check the log in {1}".format(lipofile,logfile)
            self.logger.critical(msg)
            raise RuntimeError,msg

        # Set the variable
        self.lipofile = lipofile

        return

    def get_version(self):
        """ Return the Rosetta version as a string"""
        

            

        # Get version
        version = None
        version_file = os.path.join(self.rosetta_dir,'README.version')
        if os.path.exists(version_file):
            try:
                for line in open(version_file,'r'):
                    line.strip()
                    if line.startswith('Rosetta'):
                        tversion = line.split()[1].strip()
                        # version can be 3 digits - e.g. 3.2.4 - we only care about 2
                        version = float( ".".join(tversion.split(".")[0:2]) )
                #self.logger.info( 'Your Rosetta version is: {0}'.format( version ) )
            except Exception,e:
                self.logger.critical("Error determining rosetta version from file: {0}\n{1}".format(version_file,e))
                return False
        else:
            # Version file is absent in 3.5, so we need to use the directory name
            self.logger.debug('Version file for Rosetta not found - checking to see if its 3.5 or 3.6')
            if self.rosetta_dir.endswith(os.sep): self.rosetta_dir = self.rosetta_dir[:-1]
            if self.rosetta_dir.endswith("3.5"):
                version=3.5
            # 3.6 bundles seem to look like: rosetta_2014.30.57114_bundle
            # elif re.search("rosetta_\d{4}\.\d{2}\.\d{5}_bundle",dirname):
            # Ignore as people change the directory names - just check for the presence of the folders:
            elif self._chk36(self.rosetta_dir):
                version=3.6
            else:
                self.logger.debug("Cannot determine rosetta version in directory: {0}".format(self.rosetta_dir))
                return False
        self.logger.info('Rosetta version is: {0}'.format(version))
        return version

    def _chk36(self,rosetta_dir):
        # Make sure all the expected directories are found
        #expected=frozenset(['demos','documentation','main','tools'])
        expected=frozenset(['demos','main','tools'])
        found=frozenset([os.path.basename(d) for d in os.listdir(rosetta_dir) if os.path.isdir(os.path.join(rosetta_dir,d))])
        if len(expected.intersection(found)) == len(expected):
            return True
        else:
            return False

    def get_bin_dir(self):
        """Determine the binary directory for the version"""
        assert self.rosetta_version and type(self.rosetta_version) is float,"self.rosetta_version needs to be set before calling get_bin_dir"
        assert os.path.isdir(self.rosetta_dir),"self.rosetta_dir needs to have been set before calling get_bin_dir"
        bin_dir=os.path.join(self.rosetta_dir,'rosetta_source','bin') 
        if self.rosetta_version >= 3.6:
            bin_dir = os.path.join(self.rosetta_dir,'main','source','bin')
        return bin_dir

    def idealize_cmd(self,pdbin):
        """Return command to idealize pdbin"""
        return [self.rosetta_idealize_jd2, "-database", self.rosetta_db, "-s", pdbin]

    def idealize_models(self, models, monitor):
        # Loop through each model, idealise them and get an alignment
        owd=os.getcwd()
        idealise_dir = os.path.join(self.work_dir, 'idealised_models')
        os.mkdir(idealise_dir)
        os.chdir(idealise_dir)
        self.logger.info("Idealising {0} models in directory: {1}".format(len(models),idealise_dir))
        id_scripts=[]
        id_pdbs=[]
        job_time=7200
        # WHAT ABOUT STDOUT?
        for model in models:
            # run idealise on models
            script="#!/bin/bash\n"
            if self.submit_cluster:
                script += clusterize.ClusterRun().queueDirectives(nProc=1,
                                                                  jobTime=job_time,
                                                                  queue=self.submit_queue,
                                                                  qtype=self.submit_qtype)
            script += " ".join(self.idealize_cmd(pdbin=model)) + "\n"
    
            # Get the name of the pdb that will be output
            id_pdbs.append(self.idealize_pdbout(pdbin=model,directory=idealise_dir))
            
            name=os.path.splitext(os.path.basename(model))[0]
            sname=os.path.join(idealise_dir,"{0}_idealize.sh".format(name))
            with open(sname,'w') as w: w.write(script)
            os.chmod(sname, 0o777)
            id_scripts.append(sname)
        
        # Run the jobs
        success = self.run_scripts(job_scripts=id_scripts, job_time=job_time, monitor=None)
        if not success:
            raise RuntimeError, "Error running ROSETTA in directory: {0}\nPlease check the log files for more information.".format(idealise_dir)
        # Check all the pdbs were produced - don't check with the NMR sequence as idealise can remove some residues (eg. HIS - see examples/nmr.remodel)
        if not pdb_edit.check_pdbs(id_pdbs, single=True, allsame=True):
            raise RuntimeError,"Error idealising models in directory: {0}\nInvalid models were produced!".format(idealise_dir)
        os.chdir(owd)
        return id_pdbs

    def idealize_pdbout(self,pdbin,directory=None):
        """Return the path to the pdb generated by idealize for pdbin"""
        pdir,fname = os.path.split(pdbin)
        if not directory: directory = pdir
        name,ext=os.path.splitext(fname)
        return os.path.join(directory,"{0}_0001{1}".format(name,ext))

    def modelling_cmd(self, wdir, nstruct, seed):
        """
        Return the command to run rosetta as a list suitable for subprocess
        wdir: directory to run in
        nstruct: number of structures to process
        seed: seed for this processor"""

        # Set executable
        if self.transmembrane:
            cmd = [ self.transmembrane_exe ]
        else:
            cmd = [ self.rosetta_AbinitioRelax ]

        cmd += ['-database', self.rosetta_db,
                '-in::file::fasta', self.fasta,
                '-in:file:frag3', self.frags_3mers,
                '-in:file:frag9', self.frags_9mers,
                '-out:path', wdir,
                '-out:pdb',
                '-out:nstruct', str(nstruct),
                '-out:file:silent', os.path.join( wdir, 'silent.out'),
                '-run:constant_seed',
                '-run:jran', str(seed),
                '-abinitio:relax',
                '-relax::fast'
                ]

        if self.rosetta_version >= 3.4:
            # Recommended default paramenters - see also Radius of gyration reweight
            cmd += [ "-abinitio::rsd_wt_helix", "0.5",
                     "-abinitio::rsd_wt_loop", "0.5",
                     "-use_filters", "true" ]

            if self.psipred_ss2: # not sure if this works < 3.4
                cmd += [ "-psipred_ss2", self.psipred_ss2 ]

        if self.all_atom:
            cmd += [ '-return_full_atom true', ]
        else:
            cmd += [ '-return_full_atom false' ]

        if self.transmembrane:
            cmd += [ '-in:file:spanfile', self.spanfile,
                     '-in:file:lipofile', self.lipofile,
                     '-abinitio:membrane',
                     '-membrane:no_interpolate_Mpair',
                     '-membrane:Menv_penalties',
                     '-score:find_neighbors_3dgrid',
                     '-membrane:normal_cycles', '40',
                     '-membrane:normal_mag', '15',
                     '-membrane:center_mag', '2',
                     '-mute core.io.database',
                     '-mute core.scoring.MembranePotential'
                    ]

        # Constraints file or domain constraints
        if self.constraints_file or self.domain_termini_distance  > 0:
            if self.domain_termini_distance  > 0:
                constraints_file=self.setup_domain_constraints()
            else:
                constraints_file=self.constraints_file
            if not os.path.isfile(constraints_file):
                msg="Cannot find constraints file: {0}".format(constraints_file)
                self.logger.critical(msg)
                raise RuntimeError,msg
            cmd+=['-constraints:cst_file',constraints_file,'-constraints:cst_fa_file',constraints_file]

        # Radius of gyration reweight
        if self.rad_gyr_reweight is not None:
            cmd+= ['-rg_reweight', str(self.rad_gyr_reweight) ]
        else:
            cmd+= ['-rg_reweight', "0.5" ]

        # Improve Template
        if self.improve_template:
            cmd += ['-in:file:native',
                    self.improve_template,
                    '-abinitio:steal_3mers',
                    'True',
                    '-abinitio:steal9mers',
                    'True',
                    '-abinitio:start_native',
                    'True',
                    '-templates:force_native_topology',
                    'True' ]
        #elif self.benchmark: cmd += ['-in:file:native', self.native_pdb]

        return cmd
    
    def mr_cmd(self,template,alignment,nstruct,seed):
        return [ self.rosetta_mr_protocols,
                 '-database ', self.rosetta_db,
                 '-MR:mode', 'cm',
                 '-in:file:extended_pose', '1',
                 '-in:file:fasta', self.fasta,
                 '-in:file:alignment', alignment,
                 '-in:file:template_pdb', template,
                 '-loops:frag_sizes', '9 3 1',
                 '-loops:frag_files', self.frags_9mers, self.frags_3mers,'none',
                 '-loops:random_order',
                 '-loops:random_grow_loops_by', '5',
                 '-loops:extended',
                 '-loops:remodel', 'quick_ccd',
                 '-loops:relax', 'relax',
                 '-relax:default_repeats','4',
                 '-relax:jump_move', 'true',
                 '-cm:aln_format', 'grishin',
                 '-MR:max_gaplength_to_model', '8',
                 '-nstruct', str(nstruct),
                 '-ignore_unrecognized_res',
                 '-overwrite',
                 '-run:constant_seed',
                 '-run:jran', str(seed) ]

    def nmr_remodel(self, nmr_model_in=None, ntimes=None, alignment_file=None, remodel_fasta=None, monitor=None):
        assert os.path.isfile(nmr_model_in),"Cannot find nmr_model_in: {0}".format(nmr_model_in)
        if remodel_fasta: assert os.path.isfile(remodel_fasta),"Cannot find remodel_fasta: {0}".format(remodel_fasta)
        if ntimes: assert type(ntimes) is int, "ntimes is not an int: {0}".format(ntimes)
        
        # Strip HETATM lines from PDB
        nmr_nohet=ample_util.filename_append(nmr_model_in,astr='nohet',directory=self.work_dir)
        pdb_edit.strip_hetatm(nmr_model_in,nmr_nohet)
        nmr_model_in = nmr_nohet
        self.logger.info('using NMR model: {0}'.format(nmr_model_in))
    
        if not os.path.isdir(self.models_dir): os.mkdir(self.models_dir)
        nmr_models_dir = os.path.join(self.work_dir, 'nmr_models')
        os.mkdir(nmr_models_dir)
    
        # Split NMR PDB into separate models
        nmr_models = pdb_edit.split_pdb(nmr_model_in, nmr_models_dir)
        num_nmr_models = len(nmr_models)
        self.logger.info('you have {0} models in your nmr'.format(num_nmr_models))
    
        if not ntimes: ntimes = 1000 / num_nmr_models
        nmr_process = int(ntimes)
        self.logger.info('processing each model {0} times'.format(nmr_process))
        num_models = nmr_process * num_nmr_models
        self.logger.info('{0} models will be made'.format(num_models))
        
        # Idealize all the nmr models to have standard bond lengths, angles etc
        id_pdbs = self.idealize_models(nmr_models, monitor=monitor)
        self.logger.info('{0} models were successfully idealized'.format(len(id_pdbs)))
        #id_pdbs = glob.glob(os.path.join(amopt.d['models'],"*.pdb"))
    
        owd=os.getcwd()
        remodel_dir = os.path.join(self.work_dir, 'remodelling')
        os.mkdir(remodel_dir)
        os.chdir(remodel_dir)
      
        # Sequence object for idealized models
        id_seq = ample_sequence.Sequence(pdb=id_pdbs[0])
        
        # Get the alignment for the structure - assumes all models have the same sequence
        if not alignment_file:
            # fasta sequence of first model
            remodel_seq = ample_sequence.Sequence(fasta=remodel_fasta)
            alignment_file = align_mafft(remodel_seq,id_seq,self.logger)
        
        # Remodel each idealized model nmr_process times
        self.remodel(id_pdbs, ntimes, alignment_file, monitor=monitor)
        
        os.chdir(owd)
        return

    def remodel(self, id_pdbs, ntimes, alignment_file, monitor=None):
        remodel_dir=os.getcwd()
        proc_map = self. remodel_proc_map(id_pdbs, ntimes)
        seeds = self.generate_seeds(len(proc_map))
        job_scripts = []
        dir_list = []
        job_time=7200
        for i, (id_model, nstruct) in enumerate(proc_map):
            name = "job_{0}".format(i)
            d = os.path.join(remodel_dir, name)
            os.mkdir(d)
            dir_list.append(d) # job script
            script = "#!/bin/bash\n"
            if self.submit_cluster:
                script += clusterize.ClusterRun().queueDirectives(nProc=1,
                                                                  jobTime=job_time,
                                                                  queue=self.submit_queue, 
                                                                  qtype=self.submit_qtype)
            cmd = self.mr_cmd(template=id_model, 
                              alignment=alignment_file, 
                              nstruct=nstruct, 
                              seed=seeds[i])
            script += " \\\n".join(cmd) + "\n"
            sname = os.path.join(d, "{0}.sh".format(name))
            with open(sname, 'w') as w: w.write(script)
            os.chmod(sname, 0o777)
            job_scripts.append(sname)
        
        success = self.run_scripts(job_scripts=job_scripts, job_time=job_time, monitor=None)
        if not success:
            raise RuntimeError, "Error running ROSETTA in directory: {0}\nPlease check the log files for more information.".format(remodel_dir)
    
        # Copy the models into the models directory - need to rename them accordingly
        pdbs = []
        for d in dir_list:
            ps = glob.glob(os.path.join(d, "*.pdb"))
            pdbs += ps
        
        if not len(pdbs):
            raise RuntimeError, "No pdbs after remodelling in directory: {0}\nPlease check the log files for more information.".format(remodel_dir)
        # Could rename each model so that we work out which model it came from but maybe later...
        for i, pdb in enumerate(pdbs):
            npdb = os.path.join(self.models_dir, "model_{0}.pdb".format(i))
            shutil.copy(pdb, npdb)
        return
    
    def remodel_proc_map(self, id_pdbs, ntimes):
        if self.submit_cluster: # For clusters we saturate the queue with single model jobs (ideally in batch mode) so that cluster
            # can manage the usage for us FIX
            proc_map = [(pdb, 1) for pdb in id_pdbs for _ in range(ntimes)]
        else:
            len_id_pdbs = len(id_pdbs)
            if self.nproc < len_id_pdbs:
                # if we have fewer processors then pdbs to remodel, each job is an idealised pdb that will be processed
                # on a processor nmr_process times
                proc_map = [(pdb, ntimes) for pdb in id_pdbs]
            else:
                proc_per_pdb = self.nproc / len(id_pdbs) # ignore remainder - we're dealing with a shed-load of cpus here
                if proc_per_pdb == 0: # More cpus then jobs, so we just assign one to each as in parallel case
                    proc_map = [(pdb, 1) for pdb in id_pdbs for _ in range(ntimes)]
                else:
                    jobs_per_proc = self.split_jobs(ntimes, proc_per_pdb)
                    proc_map = []
                    for pdb in id_pdbs:
                        for count in jobs_per_proc:
                            proc_map.append(pdb, count) # We need to split things so that each processor does a chunk of the work
        
                        # number of jobs that will be created on each processor
        return proc_map

    def run_scripts(self, job_scripts, job_time=None, monitor=None, chdir=True):
        # We need absolute paths to the scripts
        #job_scripts=[os.path.abspath(j) for j in job_scripts]
        return workers.run_scripts(job_scripts=job_scripts, 
                                   monitor=monitor,
                                   check_success=None,
                                   early_terminate=None,
                                   chdir=chdir,
                                   nproc=self.nproc,
                                   job_time=job_time,
                                   submit_cluster=self.submit_cluster,
                                   submit_qtype=self.submit_qtype,
                                   submit_queue=self.submit_queue,
                                   submit_array=self.submit_array,
                                   submit_max_array=self.submit_max_array)

    def setup_domain_constraints(self):
        """
        Create the file for restricting the domain termini and return the path to the file
        """
        self.logger.info('restricting termini distance: {0}'.format( self.domain_termini_distance ))
        fas = open(self.fasta)
        seq = ''
        for line in fas:
            if not re.search('>', line):
                seq += line.rstrip('\n')
        length = 0
        for x in seq:
            if re.search('\w', x):
                length += 1
                
        constraints_file = os.path.join(self.work_dir, 'constraints')
        with open(constraints_file, "w") as conin:
            conin.write('AtomPair CA 1 CA {0} GAUSSIANFUNC {1} 5.0 TAG\n'.format(length,self.domain_termini_distance))
        return constraints_file

    def set_from_dict(self, optd ):
        """
        Set the values from a dictionary
        """

        # Common variables
        self.fasta = optd['fasta']
        self.work_dir = optd['work_dir']
        self.name = optd['name']
        #self.benchmark=optd['benchmark_mode']

        # psipred secondary structure prediction
        if optd['psipred_ss2'] is not None and os.path.isfile( optd['psipred_ss2'] ):
            self.psipred_ss2 = optd['psipred_ss2']

        # Fragment variables
        self.use_homs = optd['use_homs']
        self.fragments_directory = os.path.join(optd['work_dir'],"rosetta_fragments")

        if optd['transmembrane']:

            self.transmembrane = True

            if optd['blast_dir']:
                blastpgp = os.path.join(optd['blast_dir'],"bin/blastpgp")
                blastpgp = ample_util.find_exe( blastpgp )
            else:
                blastpgp = ample_util.find_exe('blastpgp')

            # Found so set
            optd['blastpgp'] = blastpgp
            self.blastpgp = blastpgp

            # nr database
            if not os.path.exists(str(optd['nr'])) and not os.path.exists( str(optd['nr'])+".pal"):
                msg = "Cannot find the nr database: {0}\nPlease give the location with the nr argument to the script.".format( optd['nr'] )
                self.logger.critical(msg)
                raise RuntimeError, msg

            # Found it
            self.nr = optd['nr']

            self.spanfile = optd['transmembrane_spanfile']
            self.lipofile = optd['transmembrane_lipofile']
            self.octopusTopology = optd['transmembrane_octopusfile']

            # Check if we've been given files
            if  self.octopusTopology and not (os.path.isfile(self.octopusTopology)):
                msg = "Cannot find provided transmembrane octopus topology prediction: {0}".format(self.octopusTopology)
                self.logger.critical(msg)
                raise RuntimeError, msg

            if  self.spanfile and not (os.path.isfile(self.spanfile)):
                msg = "Cannot find provided transmembrane spanfile: {0}".format(self.spanfile)
                self.logger.critical(msg)
                raise RuntimeError, msg

            if self.lipofile and not (os.path.isfile(self.lipofile)):
                msg = "Cannot find provided transmembrane lipofile: {0}".format(self.lipofile)
                self.logger.critical(msg)
                raise RuntimeError, msg

            if (self.spanfile and not self.lipofile) or (self.lipofile and not self.spanfile):
                msg="You need to provide both a spanfile and a lipofile"
                self.logger.critical(msg)
                raise RuntimeError, msg
        # End transmembrane checks

        # Modelling variables
        if optd['make_models'] or optd['nmr_remodel']:

            if not optd['make_frags']:
                self.frags_3mers = optd['frags_3mers']
                self.frags_9mers = optd['frags_9mers']
                if not os.path.exists(self.frags_3mers) or not os.path.exists(self.frags_9mers):
                    msg = "Cannot find both fragment files:\n{0}\n{1}\n".format(self.frags_3mers,self.frags_9mers)
                    self.logger.critical(msg)
                    raise RuntimeError,msg

            self.nproc = optd['nproc']
            self.nmodels = optd['nmodels']
            # Set models directory
            if not optd['models_dir']:
                self.models_dir = os.path.join(optd['work_dir'], "models")
            else:
                self.models_dir = optd['models_dir']

            # Extra modelling options
            self.all_atom = optd['all_atom']
            self.domain_termini_distance = optd['domain_termini_distance']
            self.rad_gyr_reweight = optd['rg_reweight']

            if optd['improve_template'] and not os.path.exists( optd['improve_template'] ):
                msg = 'cant find template to improve'
                self.logger.critical( msg)
                raise RuntimeError(msg)
            self.improve_template = optd['improve_template']
            if optd['constraints_file']:
                if not os.path.exists(optd['constraints_file']):
                    msg = "Cannot find constraints file: {0}".format(optd['constraints_file'])
                    self.logger.critical(msg)
                    raise RuntimeError, msg
                self.constraints_file=optd['constraints_file']
                
            self.use_scwrl = optd['use_scwrl']
            self.scwrl_exe = optd['scwrl_exe']
            
            # Cluster submission stuff
            self.submit_cluster = optd['submit_cluster']
            self.submit_qtype = optd['submit_qtype']
            self.submit_queue = optd['submit_queue']
            self.submit_array = optd['submit_array']
            self.submit_max_array = optd['submit_max_array']
        return

    def set_paths(self,optd=None,rosetta_dir=None):
        if rosetta_dir and os.path.isdir(rosetta_dir):
            self.rosetta_dir=rosetta_dir
        elif 'rosetta_dir' not in optd or not optd['rosetta_dir']:
            raise RuntimeError,"rosetta_dir variable not set in amopt.d!"
        elif not os.path.isdir(optd['rosetta_dir']):
            raise RuntimeError,"Cannot find rosetta_dir directory: {0}\nPlease set the correct rosetta_dir variable to point at the top Rosetta directory.".format(optd['rosetta_dir'])
        else:
            self.rosetta_dir = optd['rosetta_dir']

        # Determine version
        if optd and 'rosetta_version' in optd and optd['rosetta_version'] is not None:
            self.logger.debug( 'Using user-supplied Rosetta version: {0}'.format(optd['rosetta_version']))
            version = optd['rosetta_version']
        else:
            version = self.get_version()
            if not version:
                msg = 'Cannot determine Rosetta version in directory: {0}'.format(self.rosetta_dir)
                self.logger.critical( msg )
                raise RuntimeError,msg

        self.rosetta_version = version

        # Find the path to the binary directory
        self.rosetta_bin=self.get_bin_dir()

        # Now set all relevant paths

        # Rosetta db
        if optd and optd['rosetta_db'] and os.path.isfile(optd['rosetta_db']):
            self.rosetta_db = optd['rosetta_db']
        else:
            if self.rosetta_version < 3.6:
                self.rosetta_db = os.path.join(self.rosetta_dir,'rosetta_database')
            else:
                self.rosetta_db = os.path.join(self.rosetta_dir,'main','database')

        if not os.path.exists(self.rosetta_db):
            msg = 'cannot find Rosetta DB: {0}'.format(self.rosetta_db)
            self.logger.critical( msg )
            raise RuntimeError,msg

        # relax
        if optd and optd['rosetta_AbinitioRelax'] and os.path.isfile(optd['rosetta_AbinitioRelax']):
            self.rosetta_AbinitioRelax = optd['rosetta_AbinitioRelax']
        else:
            self.rosetta_AbinitioRelax = self.find_binary('AbinitioRelax')

        # Set path to script
        if optd and optd['rosetta_fragments_exe'] and os.path.isfile(optd['rosetta_fragments_exe']):
            self.fragments_exe=optd['rosetta_fragments_exe']
        else:
            if self.rosetta_version == 3.3:
                self.fragments_exe = os.path.join(self.rosetta_dir,'rosetta_fragments','make_fragments.pl')
            elif self.rosetta_version  == 3.4 or self.rosetta_version  == 3.5:
                self.fragments_exe = os.path.join(self.rosetta_dir,'rosetta_tools','fragment_tools','make_fragments.pl')
            elif self.rosetta_version  == 3.6:
                self.fragments_exe = os.path.join(self.rosetta_dir,'tools','fragment_tools','make_fragments.pl')

        # Transmambrane stuff
        #if optd and optd['rosetta_membrane_abinitio2'] and os.path.isfile(optd['rosetta_membrane_abinitio2']):
        #    self.transmembrane_exe = optd['rosetta_membrane_abinitio2']
        #else:
        self.transmembrane_exe = self.find_binary('membrane_abinitio2')

        if self.rosetta_version < 3.6:
            tm_script_dir = os.path.join(self.rosetta_dir,"rosetta_source/src/apps/public/membrane_abinitio")
        else:
            tm_script_dir = os.path.join(self.rosetta_dir,'tools','membrane_tools')
        self.octopus2span = tm_script_dir + os.sep + "octopus2span.pl"
        self.run_lips = tm_script_dir + os.sep + "run_lips.pl"
        self.align_blast = tm_script_dir + os.sep + "alignblast.pl"

        if not os.path.exists(self.octopus2span) or not os.path.exists(self.run_lips) or not os.path.exists(self.align_blast):
            msg = "Cannot find the required executables: octopus2span.pl ,run_lips.pl and align_blast.pl in the directory\n" +\
            "{0}\nPlease check these files are in place".format( tm_script_dir )
            self.logger.critical(msg)
            raise RuntimeError, msg

        # for nme
        self.rosetta_cluster = self.find_binary('cluster')
        self.rosetta_mr_protocols = self.find_binary('mr_protocols')
        self.rosetta_idealize_jd2 = self.find_binary('idealize_jd2')

        return

class RosettaScoreData(object):
    
    def __init__(self):
        self.score = None
        self.rms = None
        self.maxsub = None
        self.description = None
        self.model = None
        return

class RosettaScoreParser(object):
    
    def __init__(self, directory ):
        
        self.directory = directory
        
        self.avgScore = None
        self.topScore = None
        self.avgRms = None
        self.topRms = None
        self.avgMaxsub = None
        self.topMaxsub = None
        
        self.data = []
        
        score_file = os.path.join( directory, "score.fsc")
        if not os.path.isfile(score_file):
            raise RuntimeError,"Cannot find ROSETTA score file: {0}".format(score_file)
        self.parseFile( score_file )
        
    def parseFile(self, score_file ):
        
        print "Parsing file ",score_file
        idxScore=None
        idxRms=None
        idxMaxsub=None
        idxDesc=None
        for i, line in enumerate( open(score_file, 'r') ):
            
            line = line.strip()
            
            # Read header
            if i == 0:
                for j,f in enumerate(line.split()):
                    if f=="score":
                        idxScore=j
                    elif f=="rms":
                        idxRms=j
                    elif f=="maxsub":
                        idxMaxsub=j
                    elif f=="description":
                        idxDesc=j
                
                if idxScore==None or idxRms==None or idxMaxsub==None or idxDesc==None:
                    raise RuntimeError,"Missing header field from score file: {0}".format(score_file)
                continue
                # End read header
    
            if not line: # ignore blank lines - not sure why they are there...
                continue
            
            d = RosettaScoreData()
            
            fields = line.split()
            d.score = float(fields[idxScore])
            d.rms = float(fields[idxRms])
            d.maxsub = float(fields[idxMaxsub])
            d.description = fields[idxDesc]
            #pdb = fields[31]
            
            d.model = os.path.join( self.directory, d.description+".pdb" )
            
            self.data.append( d )
        
        avg = 0
        self.topScore = self.data[0].score
        for d in self.data:
            avg += d.score
            if d.score < self.topScore:
                self.topScore = d.score
        self.avgScore  = avg / len(self.data)
        
        avg = 0
        self.topRms = self.data[0].rms
        for d in self.data:
            avg += d.rms
            if d.rms < self.topRms:
                self.topRms = d.rms
        self.avgRms  = avg / len(self.data)
        
        avg = 0
        self.topMaxsub = self.data[0].maxsub
        for d in self.data:
            avg += d.maxsub
            if d.maxsub > self.topMaxsub:
                self.topMaxsub = d.maxsub
        self.avgMaxsub  = avg / len(self.data)
        
        return
        
    def maxsubSorted(self, reverse=True ):
        return sorted( self.data, key=lambda data: data.maxsub, reverse=reverse )
     
    def rmsSorted(self, reverse=True ):
        return sorted( self.data, key=lambda data: data.rms, reverse=reverse )
    
    def rms(self, name):
        for d in self.data:
            if d.description == name:
                return d.rms
            
    def maxsub(self, name):
        for d in self.data:
            if d.description == name:
                return d.maxsub
    
    def __str__(self):
        s = "Results for: {0}\n".format(self.name)
        s += "Top score : {0}\n".format( self.topScore )
        s += "Avg score : {0}\n".format( self.avgScore )
        s += "Top rms   : {0}\n".format( self.topRms )
        s += "Avg rms   : {0}\n".format( self.avgRms )
        s += "Top maxsub: {0}\n".format( self.topMaxsub )
        s += "Avg maxsub: {0}\n".format( self.avgMaxsub )
        return s


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Set up paths. Need to do this with setUpClass, as otherwise the __file__
        variable is updated whenever the cwd is changed in a test and the next test
        gets the wrong paths.
        """
        cls.thisd =  os.path.abspath( os.path.dirname( __file__ ) )
        paths = cls.thisd.split( os.sep )
        cls.ample_dir = os.sep.join( paths[ : -1 ] )
        cls.tests_dir=os.path.join(cls.ample_dir,"tests")
        cls.testfiles_dir = os.path.join(cls.tests_dir,'testfiles')
        return

    def XtestMakeFragments(self):
        """See we can create fragments"""

        print "testing FragmentGenerator"

        optd = {}
        optd['rosetta_dir'] = "/opt/rosetta3.4"
        optd['name'] = "TOXD_"
        optd['work_dir'] =  os.getcwd()
        optd['use_homs'] =  True
        optd['make_frags'] = True
        optd['rosetta_db'] = None
        optd['rosetta_fragments_exe'] =  "/tmp/make_fragments.pl"
        #optd['rosetta_fragments_exe'] =  None
        optd['fasta'] = self.ampledir + "/examples/toxd-example/toxd_.fasta"

        optd['make_models'] = False
        optd['frags_3mers'] = None
        optd['frags_9mers'] = None
        optd['improve_template'] = None

        m = RosettaModel(optd=optd)
        m.generate_fragments()
        
        return


    def testNoRosetta(self):
        """
        Test without Rosetta
        """
        os.chdir(self.thisd) # Need as otherwise tests that happen in other directories change os.cwd()

        ## Create a dummy script
        script = "dummy_rosetta.sh"
        with open(script,"w") as f:
            content = """#!/usr/bin/env python
for i in range(10):
    f = open( "rosy_{0}.pdb".format(i), "w")
    f.write( "rosy_{0}.pdb".format(i) )
    f.close()"""
            f.write(content)
        os.chmod(script, 0o777)
        
        # Create dummy fragment files
        frags3='3mers'
        frags9='9mers'
        with open(frags3,'w') as f3,open(frags9,'w') as f9:
            f3.write(frags3+"\n")
            f9.write(frags9+"\n")

        # Set options
        optd={}
        optd['nproc'] = 3
        optd['nmodels'] = 30
        optd['work_dir'] = os.getcwd()
        optd['models_dir'] = "XXXmodelsXXX"
        optd['rosetta_db'] = None
        optd['rosetta_dir'] = "/opt/rosetta3.4"
        optd['rosetta_AbinitioRelax'] = os.path.join(os.getcwd(),script)
        optd['frags_3mers'] = frags3
        optd['frags_9mers'] = frags9
        optd['rosetta_fragments_exe'] = None
        optd['use_homs'] = None
        optd['make_models'] = True
        optd['make_frags'] =  False
        optd['fasta'] = "FASTA"
        optd['name'] = "TOXD_"
        optd['improve_template'] = None
        optd['all_atom'] = True
        optd['use_scwrl'] = False
        optd['scwrl_exe'] = ""
        optd['benchmark_mode'] = False
        optd['transmembrane'] = False
        optd['psipred_ss2'] = None
        optd['rg_reweight'] = None

        optd['domain_termini_distance'] = None
        optd['CC'] = None
        optd['improve_template'] = None

        rm = RosettaModel(optd=optd)
        mdir = rm.doModelling()
        
        os.unlink(script)
        os.unlink('seedlist')
        os.unlink(frags3)
        os.unlink(frags9)
        shutil.rmtree(mdir)
        
        return

    def XtestTransmembraneFragments(self):
        """
        Test for generating transmembrane fragments
        """

        optd = {}
        optd['work_dir'] = os.getcwd()
        optd['rosetta_dir'] = "/opt/rosetta3.4"
        optd['rosetta_fragments_exe'] = None
        optd['use_homs'] = None
        optd['make_models'] = False
        optd['make_frags'] =  True
        optd['fasta'] = "/home/Shared/2UUI/2uui.fasta"
        optd['name'] = "2uui_"
        optd['transmembrane'] = True
        optd['blast_dir'] = "/opt/blast-2.2.26"
        optd['nr'] = "/opt/nr/nr"

        fragdir=os.getcwd()+os.sep+"fragments"
        import shutil
        shutil.copy2(optd['fasta'], fragdir)

        rm = RosettaModel(optd=optd)
        rm.fragments_directory = os.getcwd()+os.sep+"fragments"
        rm.generate_tm_predict()
        
        return


def testSuite():
    suite = unittest.TestSuite()
    suite.addTest(Test('testNoRosetta'))
    return suite
    
#
# Run unit tests
if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(testSuite())

