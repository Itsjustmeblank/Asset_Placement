import maya.cmds
import PySide2 (QtWidgets, QtCore)
import random, math


# Global Variables

# preview_objects = []
# final_objects = []
# positions = []


# UI Setup

# create UI window
# add inputs: count, spacing, prefix
# add dropdown: placement mode (world / surface)
# add checkboxes: preview, collision, grouping, auto-run
# add buttons: preview, confirm, clear
# gather all inputs into settings


# Tool Logic

# preview:
    # clear preview
    # generate positions
    # create and place proxy cubes (or others geo)

# confirm:
    # clear final objects
    # create assets from positions
    # rename and move objects
    # group if enabled
    # delete preview

# clear:
    # delete preview objects
    # delete final objects


# Placement Class

# generate positions:
    # create empty list
    # loop until count reached:
        # get random position
        # if collision on → check spacing
        # add valid positions
    # return positions

# distance check:
    # calculate distance between two points


# Object Manager(Class?)

# create object:
    # duplicate or instance
    # apply name
    # return object

# group objects:
    # create group if needed
    # parent all objects


# Auto-Run

# if auto-run OFF → normal generation
# if auto-run ON:
    # generate positions first
    # create and move objects
    # group if enabled


# Wrapper (necessary?)

# run external generator
# get created objects
# if auto-run ON → reposition objects


# UI Actions

# preview button → run preview
# confirm button → run confirm
# clear button → run clear


# Run Tool

# close existing UI
# create and show new UI