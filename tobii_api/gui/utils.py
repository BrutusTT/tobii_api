import cv2

from PyQt5.QtCore       import Qt
from PyQt5.QtGui        import QImage, QPixmap


def cv_image2pixmap(image, scale = None):
    image                   = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width, channel  = image.shape
    bpl                     = channel * width
    q_image                 = QImage(image.data, width, height, bpl, QImage.Format_RGB888)
    pixmap                  = QPixmap(q_image)
    
    if scale:
        pixmap = pixmap.scaled(scale[0], scale[1], Qt.KeepAspectRatio)
    
    return pixmap
