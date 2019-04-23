import os.path as op

import cv2

from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui     import QImage, QPixmap




class VideoWidget(QLabel):


    def openVideo(self, path):

        # check if it is a file
        if not op.isfile(path):
            raise ValueError('%s is not a video file' % path)

        # open the video file
        self.video = cv2.VideoCapture(path)


    @property
    def pos_msec(self):
        return self.video.get(cv2.CAP_PROP_POS_MSEC)

    @property    
    def pos_frame(self):
        return int(self.video.get(cv2.CAP_PROP_POS_FRAMES)) - 1

    @pos_frame.setter
    def pos_frame(self, index):
        if 0 <= index < self.length:
            self.video.set(cv2.CAP_PROP_POS_FRAMES, index)
            self.updateImage()
    
    @property
    def pos_avi_ratio(self):
        return self.video.get(cv2.CAP_PROP_POS_AVI_RATIO)

    @property
    def fps(self):
        return self.video.get(cv2.CAP_PROP_FPS)
    
    @property
    def length(self):
        return int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
    
    @property
    def frame_width(self):
        return self.video.get(cv2.CAP_PROP_FRAME_WIDTH)
    
    @property
    def frame_height(self):
        return self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)

    @property
    def shape(self):
        return self.frame_width, self.frame_height
    

    @staticmethod
    def onImage(img):
        return img
    
    
    def updateImage(self):
        _, img  = self.video.read()
        
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
