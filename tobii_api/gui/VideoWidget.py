import cv2

from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui     import QImage, QPixmap

from tobii_api.video import Video




class VideoWidget(QLabel):


    def openVideo(self, path):
        self.video = Video(path)
    

    @staticmethod
    def onImage(img):
        return img
    
    
    def updateImage(self):
        _, img  = self.video.cap.read()
        
        try:
            img     = self.onImage(img)
        except Exception as e:
            print (e)

        # resize if necessary
        ratio   = img.shape[1] / img.shape[0]
        img     = cv2.resize(img, (int(self.height() * ratio), self.height()))

        # convert BGR -> RGB
        img     = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # create QImage
        img     = QImage(img, img.shape[1], img.shape[0], img.strides[0], QImage.Format_RGB888)

        # set it as background pixmap
        self.setPixmap(QPixmap.fromImage(img))
