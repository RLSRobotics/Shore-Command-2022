import cv2

cam1 = cv2.VideoCapture(0)
cam2 = cv2.VideoCapture(1)

while(True):
    ret1, frame1 = cam1.read()
    ret2, frame2 = cam2.read()

    if ret1:
        cv2.imshow('cam1', frame1)

    if ret2:
        cv2.imshow('cam2', frame2)

    cv2.waitKey(1)

cam1.release()
cam2.release()
cv2.destroyAllWindows()
