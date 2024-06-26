### Livebox Monitor icons module ###

from typing import Dict
from importlib.resources import files

import os
from PyQt6 import QtGui

import LiveboxMonitor.resources.icons

# ############# Icons #############

class LmIcon:
	__PIXMAP__: Dict[str, QtGui.QPixmap] = {}
	"""Dictionary containing every Pixmap created from
	the directory containing all the images.

	The key is formatted as below in both forms : 

		[Bare basename]
		[Bare basename]Pixmap
	
	"""

	def __getattr__(self, name: str) -> QtGui.QPixmap:
		return LmIcon.__PIXMAP__[name]

	@staticmethod
	def load():
		folder = files(LiveboxMonitor.resources.icons)
		for path in folder.iterdir():
			# Load PNG file
			data = path.read_bytes()
			bare_basename, ext = os.path.splitext(path.name)

			# Create Pixmap object
			pixmap = QtGui.QPixmap()
			pixmap.loadFromData(data)

			# Save in dedicated attribute
			LmIcon.__PIXMAP__[bare_basename] = pixmap
			LmIcon.__PIXMAP__[bare_basename + 'Pixmap'] = pixmap