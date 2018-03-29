from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QLabel, QComboBox
import sys

from Helpers import *
import qcodes as qc


class LoopsWidget(QWidget):

    def __init__(self, instruments, loops, actions, parent=None):
        """
        Constructor for AddInstrumentWidget window

        :param instruments: Dictionary shared with parent (MainWindow) to be able to add instruments to instruments
        dictionary in the MainWindow
        :param parent: specify object that created this widget
        """
        super(LoopsWidget, self).__init__()

        self.instruments = instruments
        self.loops = loops
        self.actions = actions
        self.parent = parent
        self.init_ui()
        self.show()

    def init_ui(self):
        self.setGeometry(256, 256, 360, 340)
        self.setMinimumSize(360, 340)
        self.setWindowTitle("Setup loops")
        self.setWindowIcon(QtGui.QIcon("osciloscope_icon.png"))

        labels = ["Lower limit", "Upper limit", "Num", "Step"]
        first_location = [40, 80]

        label = QLabel("Parameters", self)
        label.move(25, 25)

        for i in range(len(labels)):
            label = QLabel(labels[i], self)
            label.move(first_location[0] + i * 75, first_location[1] - 20)

        self.textbox_lower_limit = QLineEdit(self)
        self.textbox_lower_limit.move(first_location[0], first_location[1])
        self.textbox_lower_limit.resize(45, 20)

        self.textbox_upper_limit = QLineEdit(self)
        self.textbox_upper_limit.move(115, 80)
        self.textbox_upper_limit.resize(45, 20)

        self.textbox_num = QLineEdit(self)
        self.textbox_num.move(190, 80)
        self.textbox_num.resize(45, 20)

        self.textbox_step = QLineEdit(self)
        self.textbox_step.move(265, 80)
        self.textbox_step.resize(45, 20)

        label = QLabel("Sweep parameter:", self)
        label.move(25, 120)
        self.sweep_parameter_cb = QComboBox(self)
        self.sweep_parameter_cb.resize(180, 30)
        self.sweep_parameter_cb.move(45, 140)
        for name, instrument in self.instruments.items():
            for parameter in instrument.parameters:
                display_member_string = "[" + name + "] " + parameter
                value_member = instrument.parameters[parameter]
                self.sweep_parameter_cb.addItem(display_member_string, value_member)
        self.add_sweep_parameter_btn = QPushButton("Add", self)
        self.add_sweep_parameter_btn.resize(60, 30)
        self.add_sweep_parameter_btn.move(240, 140)
        self.add_sweep_parameter_btn.clicked.connect(self.add_sweep_parameter)

        label = QLabel("Loop action parameter:", self)
        label.move(25, 200)
        self.action_parameter_cb = QComboBox(self)
        self.action_parameter_cb.resize(180, 30)
        self.action_parameter_cb.move(45, 220)
        for name, instrument in self.instruments.items():
            for parameter in instrument.parameters:
                display_member_string = "[" + name + "] " + parameter
                data_member = instrument.parameters[parameter]
                self.action_parameter_cb.addItem(display_member_string, data_member)
        for name, loop in self.loops.items():
            display_member_string = "[" + name + "]"
            data_member = loop
            self.action_parameter_cb.addItem(display_member_string, data_member)
        self.add_action_parameter_btn = QPushButton("Add", self)
        self.add_action_parameter_btn.resize(60, 30)
        self.add_action_parameter_btn.move(240, 220)
        self.add_action_parameter_btn.clicked.connect(self.add_action_parameter)


        self.add_loop_btn = QPushButton("Create loop", self)
        self.add_loop_btn.move(45, 270)
        self.add_loop_btn.resize(260, 40)
        self.add_loop_btn.clicked.connect(self.create_loop)

    def create_loop(self):

        try:
            self.lower = float(self.textbox_lower_limit.text())
            self.upper = float(self.textbox_upper_limit.text())
            self.num = float(self.textbox_num.text())
            self.step = float(self.textbox_step.text())
            lp = qc.Loop(self.sweep_parameter_cb.currentData().sweep(self.lower, self.upper, num=self.num), self.step).each(self.action_parameter_cb.currentData())
        except Exception as e:
            warning_string = "Errm, looks like something went wrong ! \nHINT: Measurement parameters not set. \n"\
                             + str(e)
            show_error_message("Warning", warning_string)
        else:
            name = "loop" + str(len(self.actions)+1)
            self.loops[name] = lp
            self.actions.append(lp)
            self.parent.update_loops_preview()
            self.close()

    def add_sweep_parameter(self):
        pass

    def add_action_parameter(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LoopsWidget([])
    sys.exit(app.exec_())
