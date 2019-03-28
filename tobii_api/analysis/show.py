import os.path as op

#from tobii_api.manager import Manager

import cv2


def f(img):
    #img = img[100:240, 100:240,:]
    img = img[100:200, 100:160,:]
    #cv2.imshow("",img)
    image = img.copy()


    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img = cv2.bitwise_not(img)
    img = cv2.GaussianBlur(img, (5, 5), 0)
    _, img = cv2.threshold(img, 220, 255, cv2.THRESH_TOZERO)
    _, img = cv2.threshold(img, 220, 255, cv2.THRESH_BINARY)
    img = cv2.bitwise_not(img)

    _,contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)




    # create hull array for convex hull points
    hull = []

    # calculate points for each contour
    for i in range(len(contours)):
        # creating convex hull object for each contour
        hull.append(cv2.convexHull(contours[i], False))

    hull = sorted(hull, key=lambda x: cv2.contourArea(x))
    hull.reverse()

    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

    #for i in range(len(hull)):

    hull = hull[:2]

    # compute the center of the contour
    if hull:
        try:
            M = cv2.moments(hull[-1])
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])

            img = cv2.circle(img, (cX, cY), 1, (0, 255, 0), -1)

            img = cv2.drawContours(img, hull, 1, (0, 0, 255), 1, 8)
            #cv2.imshow("img", img)

            return 1
        except:

            return 0
            pass


#    return image

def blinkCount(a):

    list_val = []
    list_time = []
    for i in range(1,len(a)):
        split_a = a[i].split('-')
        list_val.append(int(split_a[0]))
        list_time.append(split_a[1])

    count = 1
    length = ""
    if len(list_val) > 1:
        for i in range(1, len(list_val)):
            if list_val[i - 1] == list_val[i]:
                count += 1
            else:
                length += str(list_val[i - 1]) + " repeats " + str(count) + " at time"+list_time[i-1]+", "
                count = 1
        length += ("and " + str(list_val[i]) + " repeats " + str(count)) + " at time"+list_time[i-1]

    #print(length)

    blink = 0
    b = length.split(",")
    for i in range(1, len(b)):
        if "0 repeats" in b[i]:
            c = b[i].split(" ")
            d = int(c[3])
            if d <= 4:
                print(b[i])
                blink = blink + 1

    print(blink)

def gettime(msec):
    seconds = (msec / 1000) % 60
    seconds = int(seconds)
    minutes = (msec / (1000 * 60)) % 60
    minutes = int(minutes)
    hours = (msec / (1000 * 60 * 60)) % 24

    return "%d:%d:%d" % (hours, minutes, seconds)

def main():

    #     s.showFront(0.5)
    list = []
    key = 0
    camera = cv2.VideoCapture("eyesstream_10.mp4")

    # camera = cv2.VideoCapture(0)
    ret, frame = camera.read()


    while ret:
        ret, frame = camera.read()
        time = gettime(camera.get(cv2.CAP_PROP_POS_MSEC))

        if ret:
            value = f(frame)
            list.append(str(value)+"-"+time)
            #cv2.imshow('blinks counter', frame)
            key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord('q') or ret == False:
            break

        # do a little clean up

    #print(list)
    blinkCount(list)
    cv2.destroyAllWindows()
    del (camera)

if __name__ == '__main__':
    main()