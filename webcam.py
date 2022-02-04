import cv2
import numpy as np
import time

class Webcam(object):
    def __init__(UserGUI):
        #print ("WebCamEngine init")
        UserGUI.dirname = "" #for nothing, just to make 2 inputs the same
        UserGUI.cap = None
    
    def start(UserGUI):
        print("[INFO] Start webcam")
        time.sleep(1) # wait for camera to be ready
        UserGUI.cap = cv2.VideoCapture(0)
        UserGUI.valid = False
        try:
            resp = UserGUI.cap.read()
            UserGUI.shape = resp[1].shape
            UserGUI.valid = True
        except:
            UserGUI.shape = None
    
    def get_frame(UserGUI):
    
        if UserGUI.valid:
            _,frame = UserGUI.cap.read()
            frame = cv2.flip(frame,1)
            # cv2.putText(frame, str(UserGUI.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            #           (65,220), cv2.FONT_HERSHEY_PLAIN, 2, (0,256,256))
        else:
            frame = np.ones((480,640,3), dtype=np.uint8)
            col = (0,256,256)
            cv2.putText(frame, "(Error: Camera not accessible)",
                       (65,220), cv2.FONT_HERSHEY_PLAIN, 2, col)
        return frame

    def stop(UserGUI):
        if UserGUI.cap is not None:
            UserGUI.cap.release()
            print("[INFO] Stop webcam")