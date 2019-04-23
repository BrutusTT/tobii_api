import gzip
import os.path as op

from dateutil import parser
from datetime import datetime as dt


import json
import cv2
import numpy as np


dt_format = "%Y-%m-%dT%H:%m:%S%z"

# {
#     "seg_id": 1,
#     "seg_length": 36,
#     "seg_length_us": 36423699,
#     "seg_calibrating": true,
#     "seg_calibrated": true,
#     "seg_t_start": "2018-07-10T13:33:32+0000",
#     "seg_t_stop": "2018-07-10T13:34:08+0000",
#     "seg_created": "2018-07-10T13:33:32+0000",
#     "seg_end_reason": "api",
#     "seg_eyesstream": false
# }

_STR = """{
    "seg_id":          %i,
    "seg_length":      %i,
    "seg_length_us":   %i,
    "seg_calibrating": %s,
    "seg_calibrated":  %s,
    "seg_t_start":     "%s",
    "seg_t_stop":      "%s",
    "seg_created":     "%s",
    "seg_end_reason":  "%s",
    "seg_eyesstream":  %s
}"""

class Segment(object):
    
    
    
    def __init__(self, segment_path):
        self.path = segment_path
        self.data = None
        
        # segment info (segment.json)
        self.id             = 0
        self.length         = 0
        self.length_us      = 0
        self.calibrating    = False
        self.calibrated     = False
        self.t_start        = ""
        self.t_stop         = ""
        self.created        = ""
        self.end_reason     = ""
        self.eyesstream     = False
        
        self._importInfo()

    
    @property
    def front_video_file(self):
        return op.join(self.path, 'fullstream.mp4')


    @property
    def eyes_video_file(self):
        return op.join(self.path, 'eyesstream.mp4')

    
    def _importInfo(self):
        with open(op.join(self.path, 'segment.json')) as f:
            data = json.load(f)

            # remove the seq_ prefix
            for name in data:
                setattr(self, name[4:], data[name])
                
            self.t_start = parser.parse(self.t_start)
            self.t_stop  = parser.parse(self.t_stop)
    
    
    def loadData(self):
        with gzip.open(op.join(self.path, 'livedata.json.gz'), 'r') as f:
            self.data = [json.loads('[%s]' % l)[0] for l in str(f.read().decode('utf-8')).split('\n') if l]


    def showFront(self, scale = 1.0):
        cap = cv2.VideoCapture(self.front_video_file)

        while cap.isOpened():

            # Capture frame-by-frame
            _, frame = cap.read()

            frame = cv2.resize(frame, (int(frame.shape[1] * scale), int(frame.shape[0] * scale)))

            cv2.imshow("%s - %s" % (self.id, self.created), frame)
        
            # stop if q is pressed            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


    def showEyes(self, scale = 1.0):
        cap = cv2.VideoCapture(self.eyes_video_file)

        while cap.isOpened():

            # Capture frame-by-frame
            _, frame = cap.read()

            frame = cv2.resize(frame, (int(frame.shape[1] * scale), int(frame.shape[0] * scale)))

            cv2.imshow("%s - %s" % (self.id, self.created), frame)
        
            # stop if q is pressed            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


    def show(self, scale = 1.0):
        cap  = cv2.VideoCapture(self.front_video_file)
        cap2 = cv2.VideoCapture(self.eyes_video_file)

        while cap.isOpened() and cap2.isOpened():

            # Capture frame-by-frame
            _, frame1 = cap.read()
            _, frame2 = cap2.read()
            _, frame2 = cap2.read()

            frame1 = cv2.resize(frame1, (int(frame1.shape[1] * scale), int(frame1.shape[0] * scale)))
            frame2 = cv2.resize(frame2, (int(frame2.shape[1] * scale), int(frame2.shape[0] * scale)))

            print(frame1.shape, frame2.shape)

            frame2 = cv2.resize(frame2, (540, 120))
            
            frame  = np.concatenate((frame1, frame2), axis = 1)
            
            cv2.imshow("%s - %s" % (self.id, self.created), frame)
        
            # stop if q is pressed            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


    def process(self, func):
        result = []
        cap2 = cv2.VideoCapture(op.join(self.path, 'eyesstream.mp4'))
        while cap2.isOpened():
            _, frame2 = cap2.read()
            out = func(frame2[:240,:240,:])
            print (out)
            result.append(out)
        return result




    def __str__(self):
        return  _STR % (
                    self.id,
                    self.length,
                    self.length_us,
                    self.calibrating,
                    self.calibrated,
                    dt.strftime(self.t_start, dt_format),
                    dt.strftime(self.t_stop,  dt_format),
                    self.created,
                    self.end_reason,
                    self.eyesstream
                )




    def pd_left_timeline(self):
        result = []
        
        for x in self.data:
            if 'pd' in x and x['eye'] == 'left' and x['s'] == 0:
                result.append( (int(x['ts']), float(x['pd']) ) )
        
        return result


    def pd_right_timeline(self):
        result = []
        
        for x in self.data:
            if 'pd' in x and x['eye'] == 'right' and x['s'] == 0:
                result.append( (int(x['ts']), float(x['pd']) ) )
        
        return result


    def pd_right_stats(self):
        values = np.array([x[1] for x in self.pd_right_timeline()], np.float16)
        return np.min(values), np.max(values), np.mean(values), np.median(values)


    def pd_left_stats(self):
        values = np.array([x[1] for x in self.pd_left_timeline()], np.float16)
        return np.min(values), np.max(values), np.mean(values), np.median(values)
