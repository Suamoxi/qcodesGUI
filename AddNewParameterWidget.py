from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QLabel, QComboBox

import sys
import math

from Helpers import *
from qcodes.instrument.parameter import Parameter


class AddNewParameterWidget(QWidget):
    def __init__(self, instrument, instruments, dividers, parent=None):
        """
        Constructor for the AddNewParameterWidget class

        :param instruments: a dictionary shared with parent and mainWindow. Contains all instruments created so far
        :param parent: pointer to a widget that created this widget
        """
        super(AddNewParameterWidget, self).__init__()

        # dict of instruments shared with the mainWindow
        self.instrument = instrument
        self.instruments = instruments
        self.dividers = dividers
        # pointer to the widget that created this widget
        self.parent = parent

        self.functions = {}

        self.init_ui()
        self.show()

    def init_ui(self):
        # define starting size and position of the widget
        self.setGeometry(256, 256, 320, 260)
        self.setMinimumSize(320, 400)
        # define title and icon of the widget
        self.setWindowTitle("Create new parameter")
        self.setWindowIcon(QtGui.QIcon("img/osciloscope_icon.png"))

        # add a combo box for selecting an instrument
        label_instrument_name = QLabel("Instrument data (name): ", self)
        label_instrument_name.move(20, 10)
        self.instrument_text_box = QLineEdit(self.instrument.name, self)
        self.instrument_text_box.move(60, 30)
        self.instrument_text_box.resize(80, 40)
        self.instrument_text_box.setDisabled(True)

        label_for_parameter = QLabel("Parameter data:", self)
        label_for_parameter.move(20, 80)

        # text box for parameter name
        label_for_parameter_name = QLabel("Name", self)
        label_for_parameter_name.move(40, 100)
        self.parameter_name_text_box = QLineEdit("", self)
        self.parameter_name_text_box.move(40, 120)
        self.parameter_name_text_box.resize(50, 30)
        # text box for parameters label
        label_for_parameter_label = QLabel("Label", self)
        label_for_parameter_label.move(100, 100)
        self.parameter_label_text_box = QLineEdit("", self)
        self.parameter_label_text_box.move(100, 120)
        self.parameter_label_text_box.resize(50, 30)
        # text box for measurement units
        valid_units = {"Ampere": "A", "Volt": "V", "Ohm": "Ω", "Watt": "W", "Farad": "F", "Henry": "H", "Joule": "J",
                       "Electron-Volt": "eV", "Tesla": "T", "Hertz": "Hz", "No idea": "??"}
        label_for_parameter_measurement_unit = QLabel("Unit", self)
        label_for_parameter_measurement_unit.move(210, 100)
        self.parameter_measurement_unit_combo_box = QComboBox(self)
        self.parameter_measurement_unit_combo_box.move(170, 120)
        self.parameter_measurement_unit_combo_box.resize(120, 30)
        for name, unit in valid_units.items():
            display_member_string = "[" + name + "]"
            data_member = unit
            self.parameter_measurement_unit_combo_box.addItem(display_member_string, data_member)

        self.evaluation_function = QLineEdit("", self)
        self.evaluation_function.move(40, 180)
        self.evaluation_function.resize(250, 40)

        starting_position = [40, 240]
        # position relative to starting: x = starting_position[0] + (i%4)*30
        #                                y = starting_position[1] + (i//4)*30
        buttons = [["7"], ["8"], ["9"], ["+"],
                   ["4"], ["5"], ["6"], ["x"],
                   ["1"], ["2"], ["3"], ["-"],
                   ["0"], ["."], ["="], ["/"],
                   ["del"], ["("], [")"], ["sqrt"]]

        for index, text in enumerate(buttons):
            current_btn = QPushButton(text[0], self)
            current_btn.move(starting_position[0] + (index % 4)*30, starting_position[1] + (index // 4)*30)
            current_btn.resize(25, 25)
            current_btn.show()
            current_btn.clicked.connect(self.make_add_to_eval(text[0]))

        self.select_instrument_to_add_from = QComboBox(self)
        self.select_instrument_to_add_from.move(170, 240)
        self.select_instrument_to_add_from.resize(120, 30)
        for name, instrument in self.instruments.items():
            display_member_string = "[" + name + "]"
            data_member = instrument
            self.select_instrument_to_add_from.addItem(display_member_string, data_member)
        self.select_parameter_to_add = QComboBox(self)
        self.select_parameter_to_add.move(170, 280)
        self.select_parameter_to_add.resize(120, 30)
        self.add_selected_parameter = QPushButton("Add to eval", self)
        self.add_selected_parameter.move(170, 320)
        self.add_selected_parameter.resize(120, 30)
        self.add_selected_parameter.clicked.connect(self.make_add_to_eval("param"))

        self.save_parameter = QPushButton("Save", self)
        self.save_parameter.move(170, 360)
        self.save_parameter.resize(120, 30)
        self.save_parameter.clicked.connect(self.add_parameter_to_instrument)

        self.select_instrument_to_add_from.currentIndexChanged.connect(self.update_parameters_combobox)
        self.update_parameters_combobox()

    def update_parameters_combobox(self):
        if len(self.instruments):
            self.select_parameter_to_add.clear()
            instrument = self.select_instrument_to_add_from.currentData()
            for parameter in instrument.parameters:
                # i guess i dont need to show IDN parameter
                if parameter != "IDN" and str(instrument.parameters[parameter]) not in self.dividers:
                    display_member_string = parameter
                    data_member = instrument.parameters[parameter]
                    self.select_parameter_to_add.addItem(display_member_string, data_member)
                if str(instrument.parameters[parameter]) in self.dividers:
                    name = str(instrument.parameters[parameter])
                    display_member_string = self.dividers[name].name
                    data_member = instrument.parameters[parameter]
                    self.select_parameter_to_add.addItem(display_member_string, data_member)

    def make_add_to_eval(self, text):
        def add_to_eval_function():
            current_text = self.evaluation_function.text()
            if text in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", ".", "(", ")"]:
                self.evaluation_function.setText(current_text + text)
            elif text in ["+", "-", "/"]:
                self.evaluation_function.setText(current_text + " " + text + " ")
            elif text == "x":
                self.evaluation_function.setText(current_text + " " + "*" + " ")
            elif text == "del":
                self.evaluation_function.setText(current_text[:-1])
            elif text == "param":
                parameter = self.select_parameter_to_add.currentData()
                parameter_name = parameter.name
                instrument = self.select_instrument_to_add_from.currentData()
                instrument_name = instrument.name
                function_name = instrument_name + "_" + parameter_name
                self.functions[function_name] = self.instruments[instrument_name].parameters[parameter_name].get
                self.evaluation_function.setText(current_text + function_name + "()")
            elif text == "sqrt":
                self.evaluation_function.setText(current_text + "math.sqrt()")
        return add_to_eval_function

    def add_parameter_to_instrument(self):

        name = self.parameter_name_text_box.text()
        label = self.parameter_label_text_box.text()
        unit = self.parameter_measurement_unit_combo_box.currentData()
        get_cmd = self.evaluation_function.text()

        if name == "":
            show_error_message("Warning", "\n Please specify a name for your instrument")
            return
        if label == "":
            show_error_message("Warning", "\n Please specify a label for your instrument")
            return
        if get_cmd == "":
            show_error_message("Warning", "\n Please specify a get command for your instrument")
            return

        try:
            try:
                result = eval(get_cmd, globals(), self.functions)
            except:
                show_error_message("Warning", "Your get command is probably not gonna work")
                return
            self.instrument.add_parameter(name, label=label, unit=unit, get_cmd=lambda: eval(get_cmd, globals(),
                                                                                             self.functions))
        except Exception as e:
            show_error_message("Warning", str(e))
        else:
            print("Added parameter->{} to instrument->{}".format(name, self.instrument.name))
            self.parent.parent.make_open_instrument_edit(self.parent.instrument_name)()
            self.parent.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AddNewParameterWidget()
    ex.show()
    sys.exit(app.exec_())
