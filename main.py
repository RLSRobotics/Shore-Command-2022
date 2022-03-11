#camera, separate from command.py

import cv2
import threading

class Camera:
 
    def __init__(self, id):
        self.id = id
        self.name = "cam" + str(id)
        self.cam = cv2.VideoCapture(id)

        self._display = threading.Thread(target=self._updateFrame)
        self._display.daemon = False
        self._display.start()

    def _updateFrame(self):

        while True:
            ret, frame = self.cam.read()

            if ret:
                cv2.imshow(self.name, frame)

            cv2.waitKey(1)

if __name__ == "__main__":
    cam1 = Camera(0)
    # cam2 = Camera(1)
