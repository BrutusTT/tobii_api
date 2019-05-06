import os
import os.path as op


from tobii_api.project import Project


class Manager:
    
    
    def __init__(self, root_path):
        self.path           = root_path
        self.projects_path  = op.join(self.path, 'projects')

        # check that we are in the right place
        marker_file = op.join(self.path, 'projects.ttgp')
        if not op.exists(marker_file):
            raise ValueError('The given path [%s] is not a root for a Tobii filestructure' % self.root)


    def getProjectNames(self):
        """ Returns the list of project names """
        return [x for x in os.listdir(self.projects_path) if op.isdir(op.join(self.projects_path, x)) and x != 'None']


    def getProject(self, name):
        return Project(op.join(self.projects_path, name))


    def __len__(self):
        return len(self.getProjectNames())