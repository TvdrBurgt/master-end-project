from PyQt5.QtGui import QPen
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import numpy as np
from skimage import io
pg.setConfigOptions(imageAxisOrder="row-major")


    
# class MyCrosshairOverlay(pg.CrosshairROI):
#     def __init__(self, pos=None, size=None, **kargs):
#         self._shape = None
#         pg.ROI.__init__(self, pos, size, **kargs)
#         self.sigRegionChanged.connect(self.invalidate)
#         self.aspectLocked = True


# Load image
image = io.imread(r"grid 200 200 0.tif")

# Create image view object
snap_Widget = pg.ImageView()
snap_Widget.ui.roiBtn.hide()
snap_Widget.ui.menuBtn.hide()
snap_Widget.ui.histogram.hide()

# Get image item from image view object
snap_imageitem = snap_Widget.getImageItem()
snap_imageitem.setAutoDownsample(True)

# Get view from image view object
snap_view = snap_Widget.getView()


# Set image
snap_imageitem.setImage(image)
cross1 = pg.ROI(pos=(1000,1000), size=50, pen=QPen(Qt.red, 0), movable=False)
cross2 = pg.ROI(pos=(500,500), size=50, pen=QPen(Qt.green, 0), movable=False)
line1 = pg.ROI(pos=(1000,500), size=(1000,1), angle=0 ,pen=QPen(Qt.yellow, 0), movable=False)
snap_view.addItem(cross1)
snap_view.addItem(cross2)
snap_view.addItem(line1)
snap_view.removeItem(cross1)


if __name__ == "__main__":
    snap_Widget.show()
