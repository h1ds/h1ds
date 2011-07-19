"""Summary attribute functions for H1NF."""

import os

from h1ds_mdsplus.models import MDSPlusTree
from h1ds_summary.attributes import AttributeScript

class Kappa(AttributeScript):
    """Base class for kappa_h, v..."""

    def __init__(self, shot):
        super(Kappa, self).__init__(shot)
        h1data_model = MDSPlusTree.objects.get(name__iexact='h1data')
        self.t = h1data_model.get_tree(self.shot)
        

    def get_coil_data(self):
        if self.shot > 37042:
            psuproot = '.OPERATIONS.MAGNETSUPPLY'
        else:
            psuproot = '.OPERATIONS'

        i_main_node = self.t.getNode(psuproot+'.LCU.SETUP_MAIN:I2')
        i_sec_node = self.t.getNode(psuproot+'.LCU.SETUP_SEC:I2')

        i_main = i_main_node.data()
        i_sec = i_sec_node.data()

        coil_data = {'main':{}, 'sec':{}}
        for i in range(1,6):
            coil_data['main'][str(i)] = self.t.getNode(psuproot+'.LCU.LOG:MAIN_COIL'+str(i)).data()
            coil_data['sec'][str(i)] = self.t.getNode(psuproot+'.LCU.LOG:SEC_COIL'+str(i)).data()
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
        try:
            coil_data = self.get_coil_data()
            kappa = float(coil_data[2])/float(coil_data[4])
        except:
            kappa = float(self.t.getNode('.OPERATIONS:K_H').data())
        return (kappa, 'FLOAT')

class KappaV(Kappa):

    def do_script(self):
        try:
            coil_data = self.get_coil_data()
            kappa = float(coil_data[0])/float(coil_data[4])
        except:
            kappa = float(self.t.getNode('.OPERATIONS:K_OVF').data())
        return (kappa, 'FLOAT')

class KappaI(Kappa):

    def do_script(self):
        try:
            coil_data = self.get_coil_data()
            kappa = float(coil_data[1])/float(coil_data[4])
        except:
            kappa = float(self.t.getNode('.OPERATIONS:K_I').data())
        return (kappa, 'FLOAT')
