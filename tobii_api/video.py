import os.path as op

import cv2


class Video:
    
    
    def __init__(self, path):

        # check if it is a file
        if not op.isfile(path):
            raise ValueError('%s is not a video file' % path)

        # open the video file
        self.cap = cv2.VideoCapture(path)


    @property
    def pos_msec(self):
        return self.cap.get(cv2.CAP_PROP_POS_MSEC)

    @property    
    def pos_frame(self):
        return int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1

    @pos_frame.setter
    def pos_frame(self, index):
        if 0 <= index < self.length:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, index)
    
    @property
    def pos_avi_ratio(self):
        return self.cap.get(cv2.CAP_PROP_POS_AVI_RATIO)

    @property
    def fps(self):
        return self.cap.get(cv2.CAP_PROP_FPS)
    
    @property
    def length(self):
        return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    @property
    def frame_width(self):
        return self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    
    @property
    def frame_height(self):
        return self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    @property
    def shape(self):
        return self.frame_width, self.frame_height


    def calcTimestamp(self, index = None):
        """ Returns timestamp in ms. """
        return (index * 1000.0 / self.fps) if index else self.pos_msec


    def __del__(self):

        # release video object if we got one
        if hasattr(self, 'cap') and self.cap:
            self.cap.release()
