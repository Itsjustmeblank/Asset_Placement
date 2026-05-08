import maya.cmds
from PySide2 import QtWidgets, QtCore
import random, math


# Global Variables
preview_objects = []
final_objects = []
positions = []
placement_ui = None


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

    def get_distance(self, pos1, pos2):         #check distance for later 

        x1, y1, z1 = pos1
        x2, y2, z2 = pos2

        return math.sqrt(
            (x2 - x1) ** 2 +
            (y2 - y1) ** 2 +
            (z2 - z1) ** 2
        )
    

    def generate_preview(self):

        global preview_objects
        global positions

        self.clear_preview()

        settings = self.get_settings()

        count = settings["count"]
        spacing = settings["spacing"]
        collision = settings["collision"]

        attempts = 0
        max_attempts = 1000


        while len(positions) < count and attempts < max_attempts:

            attempts += 1


            x = random.uniform(-50, 50)                         #size option?
            z = random.uniform(-50, 50)
            y = 0

            new_pos = (x, y, z)

            valid = True


            if collision:

                for existing_pos in positions:

                    distance = self.get_distance(
                        new_pos,
                        existing_pos
                    )

                    # Reject close positions
                    if distance < spacing:

                        valid = False
                        break


            if valid:

                positions.append(new_pos)

                cube = cmds.polyCube(
                    name="previewCube_{}".format(
                        len(positions)
                    )
                )[0]

                cmds.move(x, y, z, cube)

                preview_objects.append(cube)

    def clear_preview(self):

        global preview_objects
        global positions

        if preview_objects:
            cmds.delete(preview_objects)

        preview_objects = []
        positions = []

    def confirm_placement(self):

        global final_objects
        global positions


        selected = cmds.ls(selection=True)
        if not selected:
            cmds.warning("Please select an object first.")
            return

        source_object = selected[0]


        if final_objects:
            cmds.delete(final_objects)

        final_objects = []

        settings = self.get_settings()
        prefix = settings["prefix"]

  
        for i, pos in enumerate(positions):         #duplicates

            asset = cmds.duplicate(
                source_object,
                name="{}_{}".format(prefix, i)
            )[0]

            cmds.move(
                pos[0],
                pos[1],
                pos[2],
                asset
            )
            final_objects.append(asset)


        if settings["auto_group"]:

            group_name = "{}_GRP".format(prefix)

            if not cmds.objExists(group_name):

                cmds.group(
                    empty=True,
                    name=group_name
                )

            cmds.parent(
                final_objects,
                group_name
            )
        self.clear_preview()



    def on_preview(self):

        self.generate_preview()


    def on_confirm(self):

        self.confirm_placement()


    def on_clear(self):

        self.clear_preview()



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