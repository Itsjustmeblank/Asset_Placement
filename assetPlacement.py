import maya.cmds as cmds
from PySide2 import QtWidgets, QtCore
import random, math
from shiboken2 import wrapInstance
from maya import OpenMayaUI


# Global Variables
preview_objects = []
final_objects = []
positions = []
placement_ui = None
source_asset = None

active_generator = None
area_object = None


def set_active_generator(generator_function):

    global active_generator
    active_generator = generator_function

def clear_active_generator():
    global active_generator
    active_generator = None

def get_generated_positions():

    return positions

def maya_main_window():

    main_window_ptr = OpenMayaUI.MQtUtil.mainWindow()

    return wrapInstance(
        int(main_window_ptr),
        QtWidgets.QWidget
    )

# UI Setup
class PlacementUI(QtWidgets.QDialog):

    def __init__(self):
        super(
            PlacementUI,
            self
        ).__init__(maya_main_window())

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
        self.area_input = QtWidgets.QDoubleSpinBox()
        self.area_input.setValue(25.0)

        layout.addWidget(QtWidgets.QLabel("Placement Area"))
        layout.addWidget(self.area_input)

        self.pattern_dropdown = QtWidgets.QComboBox()

        self.pattern_dropdown.addItems([
            "Random",
            "Ring",
            "Line",
            "Grid",
            "Box"       #more? wave? 
        ])

        self.seed_input = QtWidgets.QSpinBox()
        self.seed_input.setValue(1)

        layout.addWidget(QtWidgets.QLabel("Seed"))
        layout.addWidget(self.seed_input)

        layout.addWidget(QtWidgets.QLabel("Placement Pattern"))
        layout.addWidget(self.pattern_dropdown)

        self.prefix_input = QtWidgets.QLineEdit("asset")

        layout.addWidget(QtWidgets.QLabel("Asset Count"))
        layout.addWidget(self.count_input)

        layout.addWidget(QtWidgets.QLabel("Spacing"))
        layout.addWidget(self.spacing_input)

        layout.addWidget(QtWidgets.QLabel("Name Prefix"))
        layout.addWidget(self.prefix_input)

        self.preview_checkbox = QtWidgets.QCheckBox("Preview Mode")
        self.preview_checkbox.setChecked(True)

        self.collision_checkbox = QtWidgets.QCheckBox("Collision Avoidance(Random)")
        self.collision_checkbox.setChecked(True)

        self.group_checkbox = QtWidgets.QCheckBox("Auto Group")
        self.group_checkbox.setChecked(True)

        self.instance_checkbox = QtWidgets.QCheckBox("Use Instances")
        self.instance_checkbox.setChecked(True)

        layout.addWidget(self.instance_checkbox)
        layout.addWidget(self.preview_checkbox)
        layout.addWidget(self.collision_checkbox)
        layout.addWidget(self.group_checkbox)

        self.preview_btn = QtWidgets.QPushButton("Generate Preview")
        self.confirm_btn = QtWidgets.QPushButton("Confirm Placement")
        self.clear_btn = QtWidgets.QPushButton("Clear Scene")

        layout.addWidget(self.preview_btn)
        layout.addWidget(self.confirm_btn)
        layout.addWidget(self.clear_btn)

        self.area_object_checkbox = QtWidgets.QCheckBox(
            "Use Selected Area Object(Selection Method)"
        )

        self.area_object_checkbox.setChecked(False)

        layout.addWidget(self.area_object_checkbox)

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
            "preview": self.preview_checkbox.isChecked(),
            "collision": self.collision_checkbox.isChecked(),
            "auto_group": self.group_checkbox.isChecked(),
            "instance": self.instance_checkbox.isChecked(),
            "area": self.area_input.value(),
            "pattern": self.pattern_dropdown.currentText(),
            "seed": self.seed_input.value(),
            "area_object": self.area_object_checkbox.isChecked(),
        }

    def get_distance(self, pos1, pos2):         #check distance for later 

        x1, y1, z1 = pos1
        x2, y2, z2 = pos2

        return math.sqrt(
            (x2 - x1) ** 2 +
            (y2 - y1) ** 2 +
            (z2 - z1) ** 2
        )
    def get_random_surface_point(self):

        global area_object

        if not area_object:

            cmds.warning(
                "Select asset first, area object second."
            )

            return None

        faces = cmds.polyEvaluate(
            area_object,
            face=True
        )

        if faces <= 0:

            cmds.warning(
                "Area object must be a polygon mesh."
            )

            return None

        random_face = random.randint(
            0,
            faces - 1
        )

        face_name = "{}.f[{}]".format(
            area_object,
            random_face
        )

        verts = cmds.polyInfo(
            face_name,
            faceToVertex=True
        )

        if not verts:
            return None

        vert_indices = [
            int(v)
            for v in verts[0].split()
            if v.isdigit()
        ]

        if len(vert_indices) < 3:
            return None

        vertex_positions = []
        for index in vert_indices:

            vert = "{}.vtx[{}]".format(
                area_object,
                index
            )
            pos = cmds.pointPosition(
                vert,
                world=True
            )
            vertex_positions.append(pos)

        p1 = vertex_positions[0]
        p2 = vertex_positions[1]
        p3 = vertex_positions[2]

        r1 = random.random()
        r2 = random.random()

        sqrt_r1 = math.sqrt(r1)

        u = 1 - sqrt_r1
        v = sqrt_r1 * (1 - r2)
        w = sqrt_r1 * r2
        x = (
            u * p1[0] +
            v * p2[0] +
            w * p3[0]
        )
        y = (
            u * p1[1] +
            v * p2[1] +
            w * p3[1]
        )
        z = (
            u * p1[2] +
            v * p2[2] +
            w * p3[2]
        )
        return (x, y, z)
    
    def generate_preview(self):

        global preview_objects
        global positions
        global source_asset

        self.clear_preview()

        settings = self.get_settings()
        random.seed(settings["seed"])
        selected = cmds.ls(selection=True)
        global area_object

        if len(selected) >= 2:
            area_object = selected[1]
        else:
            area_object = None

        if selected:

            source_asset = selected[0]

        else:

            source_asset = None

        width = 1
        height = 1
        depth = 1

        if selected and not active_generator:

            temp_asset = cmds.duplicate(
                selected[0]
            )[0]

            bbox = cmds.exactWorldBoundingBox(
                temp_asset
            )

            width = abs(bbox[3] - bbox[0])
            height = abs(bbox[4] - bbox[1])
            depth = abs(bbox[5] - bbox[2])

            cmds.delete(temp_asset)

        elif active_generator:

            temp_asset = active_generator()
            if not cmds.objExists(temp_asset):

                cmds.warning(
                    "Generator must return a valid transform."
                )

                return

            bbox = cmds.exactWorldBoundingBox(
                temp_asset
            )

            width = abs(bbox[3] - bbox[0])
            height = abs(bbox[4] - bbox[1])
            depth = abs(bbox[5] - bbox[2])

            cmds.delete(temp_asset)



        count = settings["count"]
        spacing = settings["spacing"]
        collision = settings["collision"]
        area = settings["area"]

        attempts = 0
        max_attempts = 1000


        pattern = settings["pattern"]
        while len(positions) < count and attempts < max_attempts:

            attempts += 1

            if pattern == "Random":

                if settings["area_object"]:

                    surface_point = self.get_random_surface_point()

                    if not surface_point:
                        return

                    new_pos = surface_point

                else:

                    x = random.uniform(-area, area)
                    z = random.uniform(-area, area)
                    y = 0

                    new_pos = (x, y, z)

            elif pattern == "Ring":

                radius = area

                angle = (
                    (2 * math.pi / count)
                    * len(positions)
                )

                x = math.cos(angle) * radius
                z = math.sin(angle) * radius
                y = 0

                new_pos = (x, y, z)

            elif pattern == "Line":

                x = (
                    len(positions)
                    * spacing
                ) - ((count - 1) * spacing / 2)

                y = 0
                z = 0

                new_pos = (x, y, z)

            elif pattern == "Grid":

                side_count = max(
                    int(math.ceil(math.sqrt(count))),
                    1
                )

                row = len(positions) // side_count
                col = len(positions) % side_count

                x = (col * spacing) - (
                    (side_count - 1) * spacing / 2
                )

                z = (row * spacing) - (
                    (side_count - 1) * spacing / 2
                )

                y = 0

                new_pos = (x, y, z)

            elif pattern == "Box":

                side_count = max(
                    int(math.ceil(math.sqrt(count))),
                    1
                )

                spacing_offset = area / max(
                    side_count - 1,
                    1
                )

                row = len(positions) // side_count
                col = len(positions) % side_count

                x = (
                    col * spacing_offset
                ) - (area / 2)

                z = (
                    row * spacing_offset
                ) - (area / 2)

                y = 0

                new_pos = (x, y, z)

            valid = True

            if collision and pattern == "Random":

                for existing_pos in positions:

                    distance = self.get_distance(
                        new_pos,
                        existing_pos
                    )

                    if distance < spacing:

                        valid = False
                        break

            if valid:

                positions.append(new_pos)

                cube = cmds.polyCube(
                    width=width,
                    height=height,
                    depth=depth,
                    name="previewCube_{}".format(
                        len(positions)
                    )
                )[0]

                cmds.move(
                    new_pos[0],
                    new_pos[1] + (height / 2.0),
                    new_pos[2],
                    cube
                )

                preview_objects.append(cube)
                cmds.setAttr(
                    cube + ".template",
                    1
                )

                

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
        global source_asset
        global active_generator

        if not source_asset and not active_generator:

            cmds.warning(
                "Select an asset or assign a generator."
            )
            return

        if final_objects:
            cmds.delete(final_objects)

        final_objects = []

        settings = self.get_settings()
        prefix = settings["prefix"]

        for i, pos in enumerate(positions):

            # Procedural Generator
            if active_generator:

                asset = active_generator()
                if not cmds.objExists(asset):

                    cmds.warning(
                        "Generator must return a valid transform."
                    )

                    continue

            elif settings["instance"]:

                asset = cmds.instance(
                    source_asset,
                    name="{}_{}".format(prefix, i)
                )[0]

            else:

                asset = cmds.duplicate(
                    source_asset,
                    name="{}_{}".format(prefix, i)
                )[0]

            bbox = cmds.exactWorldBoundingBox(asset)

            asset_height = abs(
                bbox[4] - bbox[1]
            )

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
        self.close()


    def on_preview(self):

        self.generate_preview()


    def on_confirm(self):

        self.confirm_placement()


    def on_clear(self):

        global final_objects

        self.clear_preview()

        if final_objects:

            cmds.delete(final_objects)

        final_objects = []


def run_tool():

    global placement_ui

    try:
        placement_ui.close()
        placement_ui.deleteLater()
    except:
        pass

    placement_ui = PlacementUI()
    placement_ui.show()