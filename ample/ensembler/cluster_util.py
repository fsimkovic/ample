"""Cluster utility module"""

__author__ = "Jens Thomas, and Felix Simkovic"
__date__ = "23 Feb 2016"
__version__ = "1.0"

import glob
import logging
import os
import random

from ample.ensembler._ensembler import Cluster
from ample.util import fast_protein_cluster
from ample.util import spicker

logger = logging.getLogger(__name__)


def fast_protein_cluster(cluster_exe, max_cluster_size, models, num_clusters, nproc, work_dir):
    """Cluster models using fast_protein_cluster program
    
    Parameters
    ----------
    models : list
       A list containing structure decoys
    work_dir : str
       The work director
    num_clusters : int
       The number of clusters to produce
    max_cluster_size : int
       The maximum number of decoys per cluster
    cluster_exe : str
       The path to the spicker executable
    nproc : int
       The number of processors to use

    Returns
    -------
    list
       A list containing the clusters
    
    """
    fpc = fast_protein_cluster.FPC()
    SCORE_TYPE = 'rmsd'
    CLUSTER_METHOD = 'kmeans'
    logger.info('Running fast_protein_cluster with: score_type: {0} cluster_method: {1}'.format(SCORE_TYPE,
                                                                                                 CLUSTER_METHOD))
    fpc_rundir = os.path.join(work_dir, 'fast_protein_cluster')
    logger.info('fast_protein_cluster running in directory: {0}'.format(fpc_rundir))
    
    clusters = fpc.cluster(cluster_method=CLUSTER_METHOD,
                           fpc_exe=cluster_exe,
                           max_cluster_size=max_cluster_size,
                           models=models,
                           num_clusters=num_clusters,
                           nproc=nproc,
                           score_type=SCORE_TYPE,
                           work_dir=fpc_rundir)
    
    return clusters


def import_cluster(cluster_dir):
    """Import a cluster
    
    Parameters
    ----------
    cluster_dir : str
       The directory to store the cluster data in

    Returns
    -------
    list
       A list containing the cluster information

    Raises
    ------
    RuntimeError
       Cannot find directory
    RuntimeError
       Cannot find pdbs in directory

    """
    if not os.path.isdir(cluster_dir): 
        raise RuntimeError('Cannot find directory: {0}'.format(cluster_dir))
    
    logger.info('Importing cluster models from: {0}'.format(cluster_dir))
    
    cluster_models = glob.glob(os.path.join(cluster_dir, "*.pdb"))
    if not cluster_models: 
        raise RuntimeError("Cannot find pdbs in directory: {0}".format(cluster_dir))
    
    # Data on the cluster
    cluster = Cluster()
    cluster.method = "import"
    cluster.num_clusters = 1
    cluster.index = 1
    cluster.models = cluster_models
    
    return [cluster]


def spicker_cluster(models, cluster_dir, cluster_method_type, cluster_score_type, num_clusters,
                    max_cluster_size, cluster_exe, nproc, score_matrix=None):
    """Cluster decoys using spicker
    
    Parameters
    ----------
    models : list
       A list containing structure decoys
    cluster_dir : str
       The directory to store the cluster data in
    cluster_method_type : str
       The method to be used to cluster the decoys
    cluster_score_type : str
       The score type
    num_clusters : int
       The number of clusters to produce
    max_cluster_size : int
       The maximum number of decoys per cluster
    cluster_exe : str
       The path to the spicker executable
    nproc : int
       The number of processors to use
    score_matrix : str, optional
       The path to the score matrix to be used

    Returns
    -------
    list
       A list containing the clusters

    Raises
    ------
    RuntimeError
       No clusters returned by SPICKER

    """
            
    # Spicker Alternative for clustering
    logger.info('* Running SPICKER to cluster models *')

    spickerer = spicker.Spickerer(spicker_exe=cluster_exe)
    spickerer.cluster(models,
                      score_type=cluster_score_type,
                      run_dir=cluster_dir,
                      score_matrix=score_matrix,
                      nproc=nproc)
    logger.debug(spickerer.results_summary())
    
    ns_clusters = len(spickerer.results)
    if ns_clusters == 0:
        raise RuntimeError('No clusters returned by SPICKER')
    if ns_clusters < int(num_clusters):
        logger.critical('Requested {0} clusters but SPICKER only found {1} so using {1} clusters'.format(num_clusters, ns_clusters))
        num_clusters = ns_clusters

    clusters = []
    for i in range(num_clusters):
        cluster = spickerer.results[i]
        # We truncate the list of models to max_cluster_size. This probably 
        # needs to be redone, because as the models are ordered by their similarity
        # to the cluster centroid, we automatically select the 200 most similar 
        # to the centroid. However if the cluster is large and the models similar
        # then when theseus calculates the variances, the variances will be 
        # representative of the 200, but might not show how the models vary throughout
        # the whole cluster, which could provide better information for truncating the models.
        #
        # Note - hlfsimko - 24.02.16: Maybe we can keep the full length clusters 
        #                             and slice the list after truncation?
        cluster.num_clusters = ns_clusters
        cluster.models = cluster.models[0:max_cluster_size]
        
        clusters.append(cluster)
    
    return clusters


def random_cluster(cluster_method, max_cluster_size, models, num_clusters):
    """Cluster decoys using madness
    
    Parameters
    ----------
    cluster_method : str
       The method to be used to cluster the decoys
    max_cluster_size : int
       The maximum number of decoys per cluster
    models : list
       A list containing structure decoys
    num_clusters : int
       The number of clusters to produce

    Returns
    -------
    list
       A list containing the clusters

    Raises
    ------
    RuntimeError
       Cannot ramdonly cluster so few decoys
    RuntimeError
       Cannot find random clusters
    """
    if len(models) <= max_cluster_size + 50: # completely arbitary number
        raise RuntimeError('Cannot randomly cluster so few models')
    
    i = 0
    clusters = []
    while len(clusters) < num_clusters:
        if i > num_clusters * 3:
            raise RuntimeError('Cannot find random clusters')
        cmodels = set(random.sample(models, max_cluster_size))
        if cmodels in clusters:
            logger.debug('Found duplicate cluster')
            continue
        
        # Data on the models
        cluster = Cluster()
        cluster.method = cluster_method
        cluster.num_clusters = num_clusters
        cluster.index = i + 1
        cluster.models = list(cmodels) # convert list back to set
        
        clusters.append(cluster)
        i += 1
        
    return clusters

