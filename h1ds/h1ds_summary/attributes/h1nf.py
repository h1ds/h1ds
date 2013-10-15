"""Summary attribute functions for H1NF."""

from datetime import datetime

import MDSplus
from h1ds_summary.attributes import AttributeScript


class H1DataAttributeScript(AttributeScript):
    def __init__(self, shot):
        super(H1DataAttributeScript, self).__init__(shot)
        self.t = MDSplus.Tree('h1data', self.shot)


class Kappa(H1DataAttributeScript):
    """Base class for kappa_h, v..."""

    def get_coil_data(self):
        if self.shot > 37042:
            psuproot = '.OPERATIONS.MAGNETSUPPLY'
        else:
            psuproot = '.OPERATIONS'

        i_main_node = self.t.getNode(psuproot + '.LCU.SETUP_MAIN:I2')
        i_sec_node = self.t.getNode(psuproot + '.LCU.SETUP_SEC:I2')

        i_main = i_main_node.data()
        i_sec = i_sec_node.data()

        coil_data = {'main': {}, 'sec': {}}
        for i in range(1, 6):
            coil_data['main'][str(i)] = self.t.getNode(psuproot + '.LCU.LOG:MAIN_COIL' + str(i)).data()
            coil_data['sec'][str(i)] = self.t.getNode(psuproot + '.LCU.LOG:SEC_COIL' + str(i)).data()
        i_coils = []
        for c in range(1, 6):
            i_c = 0.0
            if True in [coil_data['main'][str(i)] == c for i in range(1, 6)]:
                i_c += i_main
            if True in [coil_data['main'][str(i)] == -c for i in range(1, 6)]:
                i_c -= i_main
            if True in [coil_data['sec'][str(i)] == c for i in range(1, 6)]:
                i_c += i_sec
            if True in [coil_data['sec'][str(i)] == -c for i in range(1, 6)]:
                i_c -= i_sec
            i_coils.append(i_c)

        if i_coils[-1] == 0:
            raise Exception

        return i_coils


class KappaH(Kappa):
    def do_script(self):
        try:
            coil_data = self.get_coil_data()
            kappa = float(coil_data[2]) / float(coil_data[4])
        except:
            kappa = float(self.t.getNode('.OPERATIONS:K_H').data())
        return kappa, 'FLOAT'


class KappaV(Kappa):
    def do_script(self):
        try:
            coil_data = self.get_coil_data()
            kappa = float(coil_data[0]) / float(coil_data[4])
        except:
            kappa = float(self.t.getNode('.OPERATIONS:K_OVF').data())
        return kappa, 'FLOAT'


class KappaI(Kappa):
    def do_script(self):
        try:
            coil_data = self.get_coil_data()
            kappa = float(coil_data[1]) / float(coil_data[4])
        except:
            kappa = float(self.t.getNode('.OPERATIONS:K_I').data())
        return kappa, 'FLOAT'


class GetTime(H1DataAttributeScript):
    def do_script(self):
        try_these = (
            "\\h1data::top.operations:h18212sl:input_07",
            "\\h1data::top.operations:h18212sl:input_01",
        )
        min_time = datetime(1970, 1, 1, 0, 0)
        for node in try_these:
            n = self.t.getNode(node)
            mds_time = n.getTimeInserted()
            # convert MDSplus time into a Python dattime object
            time_inserted = datetime.strptime(str(mds_time._getDate()), "%d-%b-%Y %H:%M:%S.%f")
            if time_inserted > min_time:
                break

        return ("'%s'" % time_inserted.strftime("%Y-%m-%d %H:%M:%S"), "DATETIME")


class GasFlow(H1DataAttributeScript):
    def do_script_for_gas_number(self, gas_number):
        try:
            mds_node = self.t.getNode('.operations.magnetsupply.lcu:setup_main:i2') #sign if it has been logged.
            if mds_node.dtype == 211: # Gas flow data not stored in setup, get from log instead.
                gas_node = self.t.getNode(".LOG.MACHINE:GAS%d_FLOW" % gas_number)
                return gas_node.data(), 'FLOAT'
            else:
                gas_node = self.t.getNode('.operations.magnetsupply.lcu:log:gas%d_set' % gas_number)
                return (0.01 * gas_node.data(), 'FLOAT')
        except:
            return 'null', 'FLOAT'


class Gas1Flow(GasFlow):
    def do_script(self):
        return self.do_script_for_gas_number(1)


class Gas2Flow(GasFlow):
    def do_script(self):
        return self.do_script_for_gas_number(2)


class Gas3Flow(GasFlow):
    def do_script(self):
        return self.do_script_for_gas_number(3)


class Gas4Flow(GasFlow):
    def do_script(self):
        return self.do_script_for_gas_number(4)


class Gas5Flow(GasFlow):
    def do_script(self):
        return self.do_script_for_gas_number(5)
