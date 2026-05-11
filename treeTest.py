import maya.cmds as cmds
import importlib
import assetPlacement
importlib.reload(assetPlacement)

def generate_tree():

    trunk = cmds.polyCylinder(
        radius=0.25,
        height=2.5,
        subdivisionsX=8
    )[0]

    cmds.move(
        0,
        1.25,
        0,
        trunk
    )

    leaves = cmds.polyCone(
        radius=1.2,
        height=3,
        subdivisionsX=8
    )[0]

    cmds.move(
        0,
        3.25,
        0,
        leaves
    )

    tree = cmds.group(
        trunk,
        leaves,
        name="tree_asset"
    )

    return tree

assetPlacement.set_active_generator(
    generate_tree
)

assetPlacement.run_tool()