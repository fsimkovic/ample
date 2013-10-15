'''
Created on Feb 28, 2013

@author: jmht
'''

# python imports
import multiprocessing
import os
import sys

# our imports
import ample_util


def worker( inqueue, early_terminate=False, check_success=None ):
    """
    Worker process to run MrBump jobs until no more left.
    
    Args:
    inqueue -- a python Queue object
    early_terminate -- bool - terminate on first success or continue running
    
    Returns:
    0 if molecular replacement worked
    1 if nothing found
    
    We keep looping, removing jobs from the inqueue until there are no more left.
    
    REM: This needs to import the main module that it lives in so maybe this should
    live in a separate module?
    """
    
    if early_terminate:
        assert callable( check_success )
    
    while True:
        if inqueue.empty():
            print "worker {0} got empty inqueue".format( multiprocessing.current_process().name )
            break

        # Got a script so run
        job = inqueue.get()
        
        # Get name from script
        print "Worker {0} running job {1}".format (multiprocessing.current_process().name, job )
        jobname = os.path.splitext( os.path.basename( job ) )[0]

        retcode = ample_util.run_command( [ job ], logfile=jobname + ".log", dolog=False )
        
        # Can we use the retcode to check?
        # REM - is retcode object
        if retcode != 0:
            print "WARNING! Worker {0} got retcode {1}".format( multiprocessing.current_process().name, retcode )
        else:
            print "Worker {0} got successful retcode {1}".format( multiprocessing.current_process().name, retcode )
            
        # Now check the result if early terminate
        if early_terminate:
            if check_success( job ):
                print "Worker {0} job succeeded".format( multiprocessing.current_process().name )
                #return 0
                sys.exit(0)
        
    #print "worker {0} FAILED!".format(multiprocessing.current_process().name)
    #return 1
    sys.exit(1)
##End worker

# No tests here as the main module needs to be importable