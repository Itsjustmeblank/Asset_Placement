import maya.cmds
from PySide2 import QtWidgets, QtCore
import random, math


# Global Variables
preview_objects = []
final_objects = []
positions = []


# UI Setup
class PlacementUI(QtWidgets.QWidget):

    def __init__(self):
        super(PlacementUI, self).__init__()

        self.setWindowTitle("Asset Placement Tool")
        self.setMinimumWidth(300)

        self.build_ui()
        self.connect_signals()


    def build_ui(self):

        layout = QtWidgets.QVBoxLayout()


        self.count_input = QtWidgets.QSpinBox()
        self.count_input.setValue(10)

        self.spacing_input = QtWidgets.QDoubleSpinBox()
        self.spacing_input.setValue(2.0)

        self.prefix_input = QtWidgets.QLineEdit("asset")

        layout.addWidget(QtWidgets.QLabel("Asset Count"))
        layout.addWidget(self.count_input)

        layout.addWidget(QtWidgets.QLabel("Spacing"))
        layout.addWidget(self.spacing_input)

        layout.addWidget(QtWidgets.QLabel("Name Prefix"))
        layout.addWidget(self.prefix_input)



        self.mode_dropdown = QtWidgets.QComboBox()
        self.mode_dropdown.addItems(["world", "surface"])
        self.mode_dropdown.setCurrentText("world")

        layout.addWidget(QtWidgets.QLabel("Placement Mode"))
        layout.addWidget(self.mode_dropdown)



        self.preview_checkbox = QtWidgets.QCheckBox("Preview Mode")
        self.preview_checkbox.setChecked(True)

        self.collision_checkbox = QtWidgets.QCheckBox("Collision Avoidance")
        self.collision_checkbox.setChecked(True)

        self.group_checkbox = QtWidgets.QCheckBox("Auto Group")
        self.group_checkbox.setChecked(True)

        self.autorun_checkbox = QtWidgets.QCheckBox("Auto-Run Placement")
        self.autorun_checkbox.setChecked(False)

        layout.addWidget(self.preview_checkbox)
        layout.addWidget(self.collision_checkbox)
        layout.addWidget(self.group_checkbox)
        layout.addWidget(self.autorun_checkbox)



        self.preview_btn = QtWidgets.QPushButton("Generate Preview")
        self.confirm_btn = QtWidgets.QPushButton("Confirm Placement")
        self.clear_btn = QtWidgets.QPushButton("Clear Scene")

        layout.addWidget(self.preview_btn)
        layout.addWidget(self.confirm_btn)
        layout.addWidget(self.clear_btn)

        self.setLayout(layout)


    def connect_signals(self):
        self.preview_btn.clicked.connect(self.on_preview)
        self.confirm_btn.clicked.connect(self.on_confirm)
        self.clear_btn.clicked.connect(self.on_clear)


    def get_settings(self):
        return {
            "count": self.count_input.value(),
            "spacing": self.spacing_input.value(),
            "prefix": self.prefix_input.text(),
            "mode": self.mode_dropdown.currentText(),
            "preview": self.preview_checkbox.isChecked(),
            "collision": self.collision_checkbox.isChecked(),
            "auto_group": self.group_checkbox.isChecked(),
            "auto_run": self.autorun_checkbox.isChecked(),
        }


#temp.
    def on_preview(self):
        print("Preview:", self.get_settings())

    def on_confirm(self):
        print("Confirm:", self.get_settings())

    def on_clear(self):
        print("Clear clicked") #



# Tool Logic
    def generate_preview(self):

        global preview_objects
        global positions


        self.clear_preview()

        settings = self.get_settings()
        count = settings["count"]

        for i in range(count):


            x = random.uniform(-10, 10)
            z = random.uniform(-10, 10)
            y = 0

            # Store position
            positions.append((x, y, z))

            cube = cmds.polyCube(name="previewCube_{}".format(i))[0]
            cmds.move(x, y, z, cube)
            preview_objects.append(cube)

    def clear_preview(self):

        global preview_objects  #required?
        global positions

        if preview_objects:
            cmds.delete(preview_objects)

        preview_objects = []
        positions = []

# Placement Class
    def confirm_placement(self):

        global final_objects
        global positions


        if final_objects:
            cmds.delete(final_objects)

        final_objects = []

        settings = self.get_settings()
        prefix = settings["prefix"]


        for i, pos in enumerate(positions):


            asset = cmds.polySphere(                            #TEST
                name="{}_{}".format(prefix, i)
            )[0]


            cmds.move(pos[0], pos[1], pos[2], asset)            #TEST


            final_objects.append(asset)


        self.clear_preview()
# Object Manager
    def on_preview(self):
        self.generate_preview()


    def on_confirm(self):
        self.confirm_placement()


    def on_clear(self):
        self.clear_preview()
# Wrapper (necessary?)

# run external generator
# get created objects
# if auto-run ON → reposition objects


# UI Actions

# preview button → run preview
# confirm button → run confirm
# clear button → run clear


# Run Tool
def run_tool():
    global placement_ui

    try:
        placement_ui.close()
    except:
        pass

    placement_ui = PlacementUI()
    placement_ui.show()

run_tool()