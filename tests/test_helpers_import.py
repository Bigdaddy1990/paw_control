import importlib
import os
import sys

sys.path.insert(0, os.path.abspath("."))


def test_helpers_importable():
    importlib.import_module("custom_components.pawcontrol.helpers")
