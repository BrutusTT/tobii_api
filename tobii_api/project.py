import os
import os.path as op

import json

from tobii_api.recording import Recording


class Project:
    
    
    def __init__(self, project_path):
        self.path       = project_path
        self.path_cal   = op.join(self.path, 'calibrations')
        self.path_par   = op.join(self.path, 'participants')
        self.path_rec   = op.join(self.path, 'recordings')

        # check that we are in the right place
        marker_file = op.join(self.path, 'project.json')
        if not op.exists(marker_file):
            raise RuntimeError('The given path [%s] is not a project' % self.path)
        
        
        self.uid     = ''
        self.info    = {}
        self.created = ''

        self._importInfo(marker_file)
    

    def _importInfo(self, project_json):
        """ Mostly a sanity check for the project json file. """
        
        with open(project_json) as f:
            data = json.load(f)
            
            self.uid  = data['pr_id']
            self.info = {
                            'CreationDate': data['pr_info']['CreationDate'],
                            'EagleId':      data['pr_info']['EagleId'],
                            'Name':         data['pr_info']['Name']
                }
            self.created = data['pr_created']


    def getRecordingNames(self):

        # no recordings without a recording path
        if not op.exists(self.path_rec):
            return []
            
        
        return [x for x in os.listdir(self.path_rec) if op.isdir(op.join(self.path_rec, x)) and x != 'None']


    def hasRecordings(self):
        return len(self.getRecordingNames()) > 0


    def getRecording(self, name):
        filepath = op.join(self.path_rec, name)
        if not op.isdir(filepath):
            return None

        return Recording(op.join(self.path_rec, name))
