'''
Useful manipulations on PDB files
'''

# Python imports
import os
import types
import unittest

# our imports
import pdb_edit
import pdb_model

class residueSequenceMap( object ):
    """Class for handling mapping between model and native residue indices.
    
     """
    
    def __init__( self, refPdb=None, targetPdb=None ):
        
        
        self.refResSeq = []
        self.refSequence = None
        self.refCAlphaMask = []
        self.refBbMask = []
        self.refOffset = None
        self._refIncomparable = None # List of atoms in the model that cannot be compared to the model
        
        self.targetResSeq = []
        self.targetSequence = None
        self.targetCAlphaMask = []
        self.targetBbMask = []
        self.targetOffset = None # Where the matched part of the sequences starts in the model
        self._targetIncomparable = None # List of atoms in the model that cannot be compared to the native
        
        self.lenMatch = None
        
        # Like this just for testing
        if refPdb and targetPdb:
            self.calc_map(refPdb, targetPdb)
        
        return
    
    def ref2target( self, refResSeq ):
        """Return the target resSeq for the given reference resSeq.
        This will calculate a resSeq in the target if there isn't one.
        """
        
        # Work out how many residues from the start of the matching region this residue is in the target
        indent = refResSeq - self.refResSeq[ self.refOffset ]
        
        # calculate the corresponding index in the reference
        targetResSeq = self.targetResSeq[ self.targetOffset ] + indent
        
        ## paranoid check
        #if 0 < self.targetOffset + indent < len( self.targetResSeq ):
        #    assert targetResSeq == self.targetResSeq[ self.targetOffset + indent ]
        
        return targetResSeq
         
    def target2ref( self, targetResSeq ):
        """Return the referece resSeq for the given target resSeq.
        This will calculate a resSeq in the reference if there isn't one.
        """
        
        # Work out how many residues from the start of the matching region this residue is in the target
        indent = targetResSeq - self.targetResSeq[ self.targetOffset ]
        
        refResSeq = self.refResSeq[ self.refOffset ] + indent
        
        ## paranoid check
        #if 0 < self.refOffset + indent < len( self.refResSeq ):
        #    assert refResSeq == self.refResSeq[ self.refOffset + indent ]
        
        return refResSeq

    def targetIncomparable( self, cAlphaMask=True, bbMask=False ):
        """Return a list of the resSeq in the target that cannot be compared to the reference.
        This includes any where there isn't a corresponding residue in the reference, or there isn't a c-alpha
        or backbone atom in either (if cAlphaMask or bbMask is set)
        """
        
        if self._targetIncomparable == None:
            
            self._targetIncomparable = []
            for i, resSeq in enumerate( self.targetResSeq ):
                
                # Before the start of the matching region
                if i < self.targetOffset:
                    self._targetIncomparable.append( resSeq )
                    continue
                
                # After end of matching region
                if i > self.lenMatch + 1:
                    self._targetIncomparable.append( resSeq )
                    continue
                
                # In matching region but no C-alpha
                if cAlphaMask:
                    if self.targetCAlphaMask[ i ]:
                        self._targetIncomparable.append( resSeq )
                        continue
                    
                # In matching region but no complete bbatoms
                if bbMask:
                    if self.targetBbMask[ i ]:
                        self._targetIncomparable.append( resSeq )
                        continue
                
                # Matching residues in reference
                refResSeq = self.target2ref( resSeq )
                try:
                    j = self.refResSeq.index( refResSeq )
                except ValueError:
                    # A residue that isn't actually in the reference
                    self._targetIncomparable.append( resSeq )
                    continue
                
                # No C-Alpha
                if cAlphaMask:
                    if self.refCAlphaMask[ j ]:
                        self._targetIncomparable.append( resSeq )
                        continue
                    
                # No bbMask
                if bbMask:
                    if self.refBbMask[ j ]:
                        self._targetIncomparable.append( resSeq )
                        continue
            
        return self._targetIncomparable

    def refIncomparable( self, cAlphaMask=True, bbMask=False ):
        """Return a list of the resSeq in the reference that cannot be compared to the target.
        This includes any where there isn't a corresponding residue in the target, or there isn't a c-alpha
        or backbone atom in either (if cAlphaMask or bbMask is set)
        """
        
        if self._refIncomparable == None:
            self._refIncomparable = []
            for i, resSeq in enumerate( self.refResSeq ):
                
                # Before the start of the matching region
                if i < self.refOffset:
                    self._refIncomparable.append( resSeq )
                    continue

                # After end of matching region
                if i > self.lenMatch + 1:
                    self._refIncomparable.append( resSeq )
                    continue

                # In matching region but no C-alpha
                if cAlphaMask:
                    if self.refCAlphaMask[ i ]:
                        self._refIncomparable.append( resSeq )
                        continue
                    
                # In matching region but no complete bbatoms
                if bbMask:
                    if self.refBbMask[ i ]:
                        self._refIncomparable.append( resSeq )
                        continue
                
                # Matching residues in reference
                targetResSeq = self.ref2target( resSeq )
                try:
                    j = self.targetResSeq.index( targetResSeq )
                except ValueError:
                    # A residue that isn't actually in the reference
                    self._refIncomparable.append( resSeq )
                    continue
                
                # No C-Alpha
                if cAlphaMask:
                    if self.targetCAlphaMask[ j ]:
                        self._refIncomparable.append( resSeq )
                        continue
                    
                # No bbMask
                if bbMask:
                    if self.targetBbMask[ j ]:
                        self._refIncomparable.append( resSeq )
                        continue
            
        return self._refIncomparable

    def __str__(self):
        me = {}
        for slot in dir(self):
            attr = getattr(self, slot)
            if not slot.startswith("__") and not ( isinstance(attr, types.MethodType) or
              isinstance(attr, types.FunctionType) ):
                me[slot] = attr
        
        s = self.__repr__() + "\n"
        for k in sorted( me.keys() ):
            s += "{0}: {1}\n".format( k, me[k]  )
        return s
    
    def calc_map( self, nativePdb, modelPdb ):
        
        self.refSequence, self.refResSeq, self.refCAlphaMask = self.read_pdb( nativePdb )
        self.targetSequence, self.targetResSeq, self.targetCAlphaMask = self.read_pdb( modelPdb )
        
        self._calc_map()
        
        return
    
    def _calc_map( self ):
        """Return a ResSeqMap mapping the index of a residue in the model to the corresponding residue in the native.
        Only works if 1 chain in either file and with standard residues
        """
        
        if len(self.refSequence) < 10 or len(self.targetSequence) < 10:
            raise RuntimeError,"Very short sequences - this will not work!"
        
        # Find where they match at the start
        self.refOffset, self.targetOffset = self._calcOffset( self.refSequence, self.targetSequence )
        
        self.lenMatch = self._lenMatch()
        
        return
    
    def _calcOffset(self, refSequence, targetSequence, reverse=False ):
        
        # The window of AA we used to check for a match    
        PROBE_LEN = 10
        
        # MAXINSET is the max number of AA into the sequence that we will go searching for a match - i.e. if more
        # then MAXINSET AA at the start are non-matching, we won't find the match 
        l = len( targetSequence ) if len( targetSequence ) < len( refSequence ) else len( refSequence )
        MAXINSET=30 if l > 30 else ( l - PROBE_LEN )
        
        # If checking from the end, reverse the strings
        if reverse:
            refSequence = refSequence[::-1]
            targetSequence = targetSequence[::-1]
        
        got=False
        for targetOffset in range( MAXINSET + 1 ):
            probe = targetSequence[ targetOffset : targetOffset+PROBE_LEN ]
            #print "PROBE ",probe
            for refOffset in range( MAXINSET + 1 ):
                #print "TEST ",self.refSequence[ refOffset:refOffset+PROBE_LEN ]
                if refSequence[ refOffset:refOffset+PROBE_LEN ] == probe:
                    got=True
                    break
            
            if got:
#                 print "GOT MODEL MATCH AT i,j ",targetOffset,refOffset
                break
            
        if not got:
            raise RuntimeError,"Could not calculate map!"
        
        return ( refOffset, targetOffset )
    
    def _lenMatch(self):
        refBackOffset, targetBackOffset = self._calcOffset( self.refSequence, self.targetSequence, reverse=True )
        #print "Got refBackOffset, ", self.refBackOffset
        #print "Got targetBackOffset ", self.targetBackOffset
        # Calculate match from the residue numbers - use reference for now
        return self.refResSeq[ len(self.refSequence) - 1 - refBackOffset ] - self.refResSeq[ self.refOffset ] + 1

    def fromInfo(self, refInfo=None, refChainID=None, targetInfo=None, targetChainID=None, modelIdx=0):
        """Create a map from 2 info objects"""
        
        # Determine index of chain so we know where to get the data from
        nativeIdx = refInfo.models[ modelIdx ].chains.index( refChainID )

        self.refResSeq = refInfo.models[ modelIdx ].resSeqs[ nativeIdx ]
        self.refSequence = refInfo.models[ modelIdx ].sequences[ nativeIdx ]
        self.refCAlphaMask = refInfo.models[ modelIdx ].caMask[ nativeIdx ]
        self.refBbMask = refInfo.models[ modelIdx ].bbMask[ nativeIdx ]
        self.refOffset = None
        self._refIncomparable = None

        modelIdx = targetInfo.models[ modelIdx ].chains.index( targetChainID )
        self.targetResSeq = targetInfo.models[ modelIdx ].resSeqs[ modelIdx ]
        self.targetSequence = targetInfo.models[ modelIdx ].sequences[ modelIdx ]
        self.targetCAlphaMask = targetInfo.models[ modelIdx ].caMask[ modelIdx ]
        self.targetBbMask =  targetInfo.models[ modelIdx ].bbMask[ modelIdx ]
        self.targetOffset = None
        self._targetIncomparable = None
        
        self._calc_map()
        
        return
    
    def read_pdb( self, pdb ):
        """Get sequence as string of 1AA
        get list of matching resSeq
        """
         
        atomTypes = [] # For checking we have all required atom types
     
        resSeq = []
        resName = []
        _atomTypes = []
        atomTypesList = []
         
        chain=None
        readingResSeq=None
        readingResName=None
        for line in open( pdb ):
             
            if line.startswith("MODEL"):
                raise RuntimeError,"FOUND MULTI_MODEL FILE!"
             
            if line.startswith("TER"):
                break
             
            if line.startswith("ATOM"):
                 
                atom = pdb_model.PdbAtom( line )
                 
                if not chain:
                    chain = atom.chainID
                 
                if atom.chainID != chain:
                    raise RuntimeError," FOUND ADDITIONAL CHAIN"
                    break
                     
                # First atom in first residue
                if readingResSeq == None:
                    readingResSeq = atom.resSeq
                    readingResName = atom.resName
                    _atomTypes.append( atom.name.strip() )
                    continue
                 
                if readingResSeq != atom.resSeq:
                    # Adding a new residue
                     
                    # Add the atom we've just finished reading
                    resName.append( readingResName )
                    resSeq.append( readingResSeq )
                    atomTypesList.append( _atomTypes )
                     
                    # Reset
                    readingResSeq = atom.resSeq
                    readingResName = atom.resName
                    _atomTypes = [ atom.name.strip() ]
                else:
                    if atom.name not in _atomTypes:
                        _atomTypes.append( atom.name.strip() )
                         
        # End reading loop
 
        # Add the atom we've just finished reading
        resName.append( readingResName )
        resSeq.append( readingResSeq )
        atomTypesList.append( _atomTypes )
         
        sequence = ""
        # Build up the sequence
        for n in resName:
            sequence += pdb_edit.three2one[ n ]
         
        # Build up the mask
        cAlphaMask = []
        for atomTypes in atomTypesList:
            if 'CA' not in atomTypes:
                cAlphaMask.append( True )
            else:
                cAlphaMask.append( False )
         
        return ( sequence, resSeq, cAlphaMask )
    
    def resSeqMatch(self):
        """Return true if the residue numbering between the model and native over the aligned region is the same"""
        
        #print self.targetResSeq[ self.targetOffset : self.targetOffset + self.lenMatch ]
        #print self.refResSeq[ self.refOffset : self.refOffset + self.lenMatch ]
        return self.targetResSeq[ self.targetOffset : self.targetOffset + self.lenMatch ] == self.refResSeq[ self.refOffset : self.refOffset + self.lenMatch ]


class Test(unittest.TestCase):


    def testResSeqMap1(self):
        """See if we can sort out the indexing between the native and model"""

        resSeqMap = residueSequenceMap()
        
        resSeqMap.targetSequence = ['G', 'G', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'F', 'F', 'F', 'F', 'F', 'F']
        resSeqMap.targetResSeq = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        resSeqMap.targetCAlphaMask = [False, False, False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False]
        
        resSeqMap.refSequence = [ 'H', 'H', 'H', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'G', 'G', 'G', 'G', 'G', 'G' ]
        resSeqMap.refResSeq = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18 ]
        resSeqMap.refCAlphaMask = [False, False, False, False, False, False, True, False, False, False, False, False, False, False, False, False, False, False, False]
        
        resSeqMap._calc_map()
        
        self.assertEqual( resSeqMap.targetOffset, 2)
        self.assertEqual( resSeqMap.refOffset, 3)
        self.assertEqual( resSeqMap._lenMatch(), 10)
        
        self.assertEqual( resSeqMap.ref2target( 0 ), -6 )
        self.assertEqual( resSeqMap.ref2target( 3 ), -3 )
        
        self.assertEqual( resSeqMap.target2ref( 1 ), 7 )
        self.assertEqual( resSeqMap.target2ref( 12 ), 18 )
        self.assertEqual( resSeqMap.target2ref( 6 ), 12 )
        
        self.assertEqual( resSeqMap.targetIncomparable(), [-5,-4,-1, 0, 7, 8, 9, 10, 11, 12] )
        self.assertEqual( resSeqMap.refIncomparable(), [ 0, 1, 2, 5, 6, 12, 13, 14, 15, 16, 17, 18 ] )
        
        # Check ends match up
        m1 = resSeqMap.targetResSeq[ resSeqMap.targetOffset ]
        n1 = resSeqMap.target2ref( m1 )
        self.assertEqual( m1, resSeqMap.ref2target(n1) )
        re = resSeqMap.refResSeq[ resSeqMap.refOffset + resSeqMap.lenMatch - 1  ]
        self.assertEqual( resSeqMap.ref2target( re ), resSeqMap.targetResSeq[ resSeqMap.targetOffset + resSeqMap.lenMatch - 1  ] )
        
        
        return
    
    def testRefSeqMap2(self):
        """See if we can sort out the indexing between the native and model"""
        
        
        nativePdb = "../tests/testfiles//2XOV.pdb"
        modelPdb = "../tests/testfiles/2XOV_S_00000001.pdb" 
        
        resSeqMap = residueSequenceMap( nativePdb, modelPdb )
        
        self.assertEqual( 181, resSeqMap._lenMatch() )
        # Check ends match up
        m1 = resSeqMap.targetResSeq[ resSeqMap.targetOffset ]
        n1 = resSeqMap.target2ref( m1 )
        self.assertEqual( m1, resSeqMap.ref2target(n1) )
        re = resSeqMap.refResSeq[ resSeqMap.refOffset + resSeqMap.lenMatch - 1  ]
        self.assertEqual( resSeqMap.ref2target( re ), resSeqMap.targetResSeq[ resSeqMap.targetOffset + resSeqMap.lenMatch - 1  ] )
        
        return
    
    def testResSeqMap3(self):
        """See if we can sort out the indexing between the native and model"""
        
        
        nativePdb = "../tests/testfiles/2UUI.pdb"
        modelPdb = "../tests/testfiles/2UUI_S_00000001.pdb"
        
        PE = pdb_edit.PDBEdit()
        chainA = "2UUI_A.pdb"
        PE.extract_chain( nativePdb, chainA, chainID='A' )
        chainAstd = "2UUI_A_std.pdb"
        PE.standardise(chainA, chainAstd)
        
        resSeqMap = residueSequenceMap( chainA, modelPdb )
        
        self.assertEqual( 156, resSeqMap._lenMatch() )

        
        nativeMask = [ False ] * 155 + [ True ]
        self.assertEqual( resSeqMap.refCAlphaMask, nativeMask)
        
        self.assertEqual( resSeqMap.ref2target(10), 16  )
        self.assertEqual( resSeqMap.target2ref(155), 149 )
        
        # Check ends match up
        m1 = resSeqMap.targetResSeq[ resSeqMap.targetOffset ]
        n1 = resSeqMap.target2ref( m1 )
        self.assertEqual( m1, resSeqMap.ref2target(n1) )
        re = resSeqMap.refResSeq[ resSeqMap.refOffset + resSeqMap.lenMatch - 1  ]
        self.assertEqual( resSeqMap.ref2target( re ), resSeqMap.targetResSeq[ resSeqMap.targetOffset + resSeqMap.lenMatch - 1  ] )
        
        os.unlink( chainA )
        os.unlink( chainAstd )
        
        return
    
    def testResSeqMap4(self):
        """See if we can sort out the indexing between the native and model"""
        
        
        nativePdb = "/media/data/shared/coiled-coils/1K33/1K33.pdb"
        modelPdb = "/media/data/shared/coiled-coils/1K33/models/S_00000001.pdb"
        
        PE = pdb_edit.PDBEdit()
        nativePdbStd = "1K33_std.pdb"
        PE.standardise( nativePdb, nativePdbStd )
        
        nativeInfo = PE.get_info( nativePdbStd )
        modelInfo = PE.get_info( modelPdb )
        
        resSeqMap = residueSequenceMap( )
        resSeqMap.fromInfo( nativeInfo, 'A', modelInfo, 'A' )
        

        
        #os.unlink( chainA )
        #os.unlink( chainAstd )
        
        return
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
