"""Summary attribute functions for H1NF."""

import os
import MDSplus

from h1ds_summary.attributes import AttributeScript

if not 'mdsplus' in os.environ["PATH"]:
    os.environ["PATH"] += ':/usr/local/mdsplus/bin'
    os.environ["MDSPLUS_DIR"] = "/usr/local/mdsplus"
    os.environ["MDS_PATH"] = "/usr/local/mdsplus"
    os.environ["h1data_path"] = "h1data.anu.edu.au::"


class Kappa(AttributeScript):
    """Base class for kappa_h, v..."""

    def get_coil_data(self):
        if self.shot > 37042:
            psuproot = '.OPERATIONS.MAGNETSUPPLY'
        else:
            psuproot = '.OPERATIONS'

        t = MDSplus.Tree('h1data', self.shot)
        i_main_node = t.getNode(psuproot+'.LCU.SETUP_MAIN:I2')
        i_sec_node = t.getNode(psuproot+'.LCU.SETUP_SEC:I2')

        i_main = i_main_node.data()
        i_sec = i_sec_node.data()

        coil_data = {'main':{}, 'sec':{}}
        for i in range(1,6):
            coil_data['main'][str(i)] = t.getNode(psuproot+'.LCU.LOG:MAIN_COIL'+str(i)).data()
            coil_data['sec'][str(i)] = t.getNode(psuproot+'.LCU.LOG:SEC_COIL'+str(i)).data()
        i_coils = []
        for c in range(1,6):
            i_c = 0.0
            if True in [ coil_data['main'][str(i)]==c for i in range(1,6)]:
                i_c += i_main
            if True in [ coil_data['main'][str(i)]==-c for i in range(1,6)]:
                i_c -= i_main
            if True in [ coil_data['sec'][str(i)]==c for i in range(1,6)]:
                i_c += i_sec
            if True in [ coil_data['sec'][str(i)]==-c for i in range(1,6)]:
                i_c -= i_sec
        i_coils.append(i_c)
        
        if i_coils[-1] == 0:
            raise Exception

        return i_coils

class KappaH(Kappa):

    def do_script(self):
        coil_data = self.get_coil_data()
        return float(coil_data[2])/float(coil_data[4])
        
"""
    #!/usr/bin/env python

import sys, os
from numpy import mean, max, abs, array
from MDSplus import Data, mdsarray, mdsscalar

if not 'mdsplus' in os.environ["PATH"]:
    os.environ["PATH"] += ':/usr/local/mdsplus/bin'
os.environ["MDSPLUS_DIR"] = "/usr/local/mdsplus"
os.environ["MDS_PATH"] = "/usr/local/mdsplus"

mds_server = 'h1data.anu.edu.au'
mds_tree = 'H1DATA'
kappa = sys.argv[1]
shot = int(sys.argv[2])


if shot > 37042:
    PSUPROOT = '.OPERATIONS.MAGNETSUPPLY'
else:
    PSUPROOT = '.OPERATIONS'

    
Data.execute("mdsconnect('h1data.anu.edu.au')")
Data.execute("mdsopen('%(mds_tree)s',%(shot)d)" %{'mds_tree':mds_tree, 'shot':shot})
# t = Data.execute("mdsvalue('dim_of(%(mds_path)s)')" %{'mds_path':mds_path})
i_main = Data.execute("mdsvalue('%(mds_path)s')" %{'mds_path':PSUPROOT+'.LCU.SETUP_MAIN:I2'})
i_sec = Data.execute("mdsvalue('%(mds_path)s')" %{'mds_path':PSUPROOT+'.LCU.SETUP_SEC:I2'})

if (type(i_main) == mdsscalar.Float32) and (type(i_sec) == mdsscalar.Float32):
    coil_data = {'main':{}, 'sec':{}}
    for i in range(1,6):
        coil_data['main'][str(i)] = Data.execute("mdsvalue('%(mds_path)s')" %{'mds_path':PSUPROOT+'.LCU.LOG:MAIN_COIL'+str(i)})
        coil_data['sec'][str(i)] = Data.execute("mdsvalue('%(mds_path)s')" %{'mds_path':PSUPROOT+'.LCU.LOG:SEC_COIL'+str(i)})
    i_coils = []
    for c in range(1,6):
        i_c = 0.0
        if True in [ coil_data['main'][str(i)]==c for i in range(1,6)]:
            i_c += i_main
        if True in [ coil_data['main'][str(i)]==-c for i in range(1,6)]:
            i_c -= i_main
        if True in [ coil_data['sec'][str(i)]==c for i in range(1,6)]:
            i_c += i_sec
        if True in [ coil_data['sec'][str(i)]==-c for i in range(1,6)]:
            i_c -= i_sec
        i_coils.append(i_c)
        
    if i_coils[-1] == 0:
        raise Exception

    if kappa in ['h','H']:
        print float(i_coils[2])/float(i_coils[4])
    elif kappa in ['v','V']:
        print float(i_coils[0])/float(i_coils[4])
    elif kappa in ['i','I']:
        print float(i_coils[1])/float(i_coils[4])
        
else:
    output = 1.0

    if kappa in ['h','H']:
        tmp = Data.execute("mdsvalue('%(mds_path)s')" %{'mds_path':',OPERATIONS:K_H'})
        if type(tmp) == mdsscalar.Float32:
            output = tmp
    elif kappa in ['i','I']:
        tmp = Data.execute("mdsvalue('%(mds_path)s')" %{'mds_path':',OPERATIONS:K_I'})
        if type(tmp) == mdsscalar.Float32:
            output = tmp
    elif kappa in ['v','V']:
        tmp = Data.execute("mdsvalue('%(mds_path)s')" %{'mds_path':',OPERATIONS:K_OVF'})
        if type(tmp[0]) == mdsscalar.Float32 and abs(tmp[0])<2:            
            output = tmp
    print output
            

Data.execute("mdsclose()")
Data.execute("mdsdisconnect()")

    
"""
