import os.path as op

import json

from segment import Segment


class Recording(object):


# {
#     "rec_id": "i5lmnjn",
#     "rec_info": {
#         "EagleId": "a5bcb634-8401-4261-a0c1-df0d70c130f5",
#         "Name": "Recording002",
#         "Notes": ""
#     },
#     "rec_participant": "3amizpo",
#     "rec_project": "l4aqtfv",
#     "rec_state": "done",
#     "rec_segments": 1,
#     "rec_length": 26,
#     "rec_calibration": "7ledp4e",
#     "rec_created": "2018-07-04T16:42:02+0000",
#     "rec_et_samples": 1294,
#     "rec_et_valid_samples": 1278,
#     "ts_right_x": -32.5,
#     "ts_right_y": -27.0,
#     "ts_right_z": -19.0,
#     "ts_left_x": 32.5,
#     "ts_left_y": -27.0,
#     "ts_left_z": -19.0,
#     "ts_green_limit_radius": 10.0,
#     "ts_yellow_limit_radius": 12.5
# }


    def __init__(self, recording_path):
        self.path = recording_path
        
        # check that we are in the right place
        marker_file = op.join(self.path, 'recording.json')
        if not op.exists(marker_file):
            raise RuntimeError('The given path [%s] is not a project' % self.path)

        self.data_par = None
        self.data_sys = None
   
        self.uid                    = ''
        self.info                   = {}
        self.participant            = ''
        self.project                = ''
        self.state                  = ''
        self.segments               = 0
        self.length                 = 0
        self.calibration            = ''
        self.created                = ''
        self.et_samples             = 0
        self.et_valid_samples       = 0
        self.ts_right_x             = 0.0
        self.ts_right_y             = 0.0
        self.ts_right_z             = 0.0
        self.ts_left_x              = 0.0
        self.ts_left_y              = 0.0
        self.ts_left_z              = 0.0
        self.ts_green_limit_radius  = 0.0
        self.ts_yellow_limit_radius = 0.0
        self.segments_data          = []

        self._importInfo()
        self._createSegments()


    def _importInfo(self):
        
        with open(op.join(self.path, 'recording.json')) as f:
            data = json.load(f)
            for name in data:
                
                # remove the rec_ prefix
                setattr(self, name[4:] if name.startswith('rec_') else name, data[name])


        if self.segments > 0:

            with open(op.join(self.path, 'participant.json')) as f:
                self.data_par = json.load(f)
    
            with open(op.join(self.path, 'sysinfo.json')) as f:
                self.data_sys = json.load(f)


    def _createSegments(self):
        for uid in range(self.segments):
            self.segments_data.append(Segment(op.join(self.path, 'segments', str(uid+1))))
        

    def getSegment(self, uid):
        return self.segments_data[int(uid) - 1]
        
        
    def getSegmentIDs(self):
        return [ '%d' % (uid + 1) for uid in range(self.segments)]

