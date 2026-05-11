import maya.cmds as cmds
import importlib
import assetPlacement

importlib.reload(assetPlacement)

def generate_tree():

    trunk = cmds.polyCylinder()[0]
    leaves = cmds.polySphere()[0]

    cmds.move(0, 2, 0, leaves)

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