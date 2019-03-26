import os.path as op

from tobii_api.manager import Manager

import cv2


def f(img):
    
    img    = img[0:240, 0:240, :]
    image  = img.copy()
    
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


    
    img    = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    for i in range(len(hull)):
        img = cv2.drawContours(img, hull, i, (0, 0, 255), 1, 8)

        # compute the center of the contour
        try:
            M = cv2.moments(hull[i])
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
    
            img = cv2.circle(img, (cX, cY), 1, (0, 255, 0), -1)
            return 1
        except:
            return 0
            pass

#    return image
    

    
    
def main():    
    m = Manager(op.expanduser('~/software/datasets/tobii'))
    for name in m.getProjectNames():
        print (name)
    
        p = m.getProject( name)
        for rec_name in p.getRecordingNames():

            print ('\t' + rec_name)
            r = p.getRecording(rec_name)
            
            if r:
                print ('\t\t' + r.uid + '\t' + str(r.segments))
                for x in r.segments_data:
                    print (x)
                    
            
    s = m.getProject('ijkrmxv').getRecording('pzb2ix5').segments_data[0]
    s.loadData()
#     s.showFront(0.5)

    print (s.process(f))



if __name__ == '__main__':
    main()