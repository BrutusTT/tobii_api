import os.path as op
from os.path            import abspath, join, dirname

from PyQt5              import uic
from PyQt5.QtCore       import Qt
from PyQt5.QtWidgets    import QApplication, QHBoxLayout, QShortcut, QScrollBar, QVBoxLayout, QLabel,\
    QAbstractItemView
from PyQt5.QtGui        import QKeySequence

from pyqode.python.widgets      import PyCodeEdit

from tobii_api.manager              import Manager
from tobii_api.segment              import Segment
from tobii_api.gui.VideoWidget      import VideoWidget
from tobii_api.gui.navigation_model import NavigationModel, NavigationNode


tmp_code= """
def f(img):
    import cv2
    img    = img[100:240, 100:240, :]
    img    = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img    = cv2.bitwise_not(img)
    img    = cv2.GaussianBlur(img, (5,5), 0)
    _, img = cv2.threshold(img, 220, 255, cv2.THRESH_TOZERO)
    _, img = cv2.threshold(img, 220, 255, cv2.THRESH_BINARY)
    img    = cv2.bitwise_not(img)
    contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # create hull array for convex hull points
    hull   = []

    # calculate points for each contour
    for i in range(len(contours)):

        # creating convex hull object for each contour
        hull.append(cv2.convexHull(contours[i], False))

    hull = sorted(hull, key= lambda x: cv2.contourArea(x))
    hull.reverse()


    img    = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    for i in range(len(hull)):
        img = cv2.drawContours(img, hull, 1, (0, 0, 255), 1, 8)

        # compute the center of the contour
        try:
            M = cv2.moments(hull[1])
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
    
            img = cv2.circle(img, (cX, cY), 1, (0, 255, 0), -1)
            print(1)
        except:
            print(0)
            pass

    return img
"""


"""
def f(img):
    import numpy as np
    i1 = img[  0:240, 0:240, :]
    i2 = img[240:480, 0:240, :]
    i3 = img[480:720, 0:240, :]
    i4 = img[720:960, 0:240, :]
    
    img = np.zeros((480,480, 3), np.uint8)
    img[  0:240,   0:240, :] = i3
    img[  0:240, 240:480, :] = i1
    img[240:480,   0:240, :] = i4
    img[240:480, 240:480, :] = i2
    return img"""
####################################################################################################
# Main Window UI File Loading
####################################################################################################
# get the directory of this script
path                         = dirname( abspath(__file__) )

# load the UI file from the same directory as the file you are just watching
MainWindowUI, MainWindowBase = uic.loadUiType( join(path, 'mainwindow.ui') )


####################################################################################################
# Main Window Class
####################################################################################################
class MainWindow(MainWindowBase, MainWindowUI):


    def __init__(self, manager, parent = None):
        MainWindowBase.__init__(self, parent)

        self.manager = manager

        self.setupUi(self)
        self.setupConnections()


    def setupUi(self, parent):
        MainWindowUI.setupUi(self, parent)

        # content area
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.content.setLayout(layout)
        
        # add video widget
        self.contentWidget = VideoWidget()
        self.content.layout().addWidget(self.contentWidget)
 
        self.prev_code  = 'def f(img):\n    return img'
        self.te_code    = PyCodeEdit()
        self.te_code.setPlainText(self.prev_code)
        self.content.layout().addWidget(self.te_code)
         
        # footer area
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.footer.setLayout(layout)
 
        self.bar_index = QScrollBar(Qt.Horizontal)
        self.bar_index.setFocusPolicy(Qt.WheelFocus)
        self.bar_index.setMinimum(0)
        self.bar_index.setSingleStep(1)
        self.bar_index.valueChanged.connect(self.indexChanged)
        layout.addWidget(self.bar_index)
 
        self.info = QLabel()
        layout.addWidget(self.info)


        # construct navigation tree
        items = []
        for project_id in self.manager.getProjectNames():
            project           = self.manager.getProject(project_id)
            p_node            = NavigationNode(project.info['Name'])
            p_node.obj_data   = project
            items.append(p_node)

            for r_id in sorted(p_node.obj_data.getRecordingNames()):
                recording       = p_node.obj_data.getRecording(r_id)

                if recording:
                    r_node          = NavigationNode(r_id)
                    r_node.obj_data = recording
 
                    p_node.addChild(r_node)
                    for segment_id in r_node.obj_data.getSegmentIDs():
                        s_node          = NavigationNode(segment_id)
                        s_node.obj_data = r_node.obj_data.getSegment(segment_id)
                        r_node.addChild(s_node)
                
         
        self.treeView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.treeView.setUniformRowHeights(True)
        self.treeView.setModel(NavigationModel(items))

        # design the view
        self.treeView.header().hide()                    # hide header
        self.treeView.expandToDepth(0)                   # expand first level


    def setupConnections(self):

        # shortcuts
        self.sc_next = QShortcut(QKeySequence("Right"), self)
        self.sc_next.activated.connect(self.nextImage)

        self.sc_prev = QShortcut(QKeySequence("Left"), self)
        self.sc_prev.activated.connect(self.prevImage)


        self.treeView.doubleClicked.connect(self.navigation_doubleClicked)


    def navigation_doubleClicked(self, _):        
        item = self.treeView.selectedIndexes()[0]
        obj  = item.internalPointer().obj_data

        if hasattr(obj, 'segments') and obj.segments_data:
            obj = obj.segments_data[0]

        if hasattr(obj, 'eyes_video_file'):
            self.setSegment(obj)
    
    
    def applyCode(self):
        code = self.te_code.toPlainText()
        if self.prev_code != code:
            try:
                exec(code, globals(), locals())
                self.contentWidget.onImage = locals()['f']
            except Exception as e:
                print(e)


    def prevImage(self):
        self.bar_index.setValue(self.bar_index.value() - 1)


    def nextImage(self):
        self.bar_index.setValue(self.bar_index.value() + 1)


    def setVideo(self, path):
        self.contentWidget.openVideo(path)
        self.bar_index.setMaximum(self.contentWidget.length)


    def indexChanged(self, value):
        self.applyCode()
        video           = self.contentWidget
        video.pos_frame = value

        info_msg = []
        info_msg.append('FPS:   %s'             % video.fps)
        info_msg.append('Frame: %d / %d (%.4f)' % (video.pos_frame+1, video.length, video.pos_msec))

        self.info.setText('\n'.join(info_msg))


    def setSegment(self, segment):
        self.setVideo(segment.eyes_video_file)
        self.bar_index.setValue(0)
        self.indexChanged(0)


####################################################################################################
# Main Function
####################################################################################################
def main():
    import sys
    
    # get the segment
    m = Manager(op.expanduser('~/software/datasets/cls/Tobii'))
    s = m.getProject('ijkrmxv').getRecording('dyswx3p').getSegment('1')
    s.loadData()

    # start app
    app = QApplication(sys.argv)
    app.processEvents()
    
    # initialize MainWindow
    mw = MainWindow(m)
    mw.setSegment(s)
    mw.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()