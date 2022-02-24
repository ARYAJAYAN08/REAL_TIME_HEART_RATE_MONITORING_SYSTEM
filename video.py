import cv2
import numpy as np
import time

class Video(object):
    def __init__(UserGUI):
        UserGUI.dirname = ""
        UserGUI.cap = None
        t0 = 0
        
    def start(UserGUI):
        print("Start video")
        if UserGUI.dirname == "":
            print("invalid filename!")
            return
            
        UserGUI.cap = cv2.VideoCapture(UserGUI.dirname)
        fps = UserGUI.cap.get(cv2.CAP_PROP_FPS)
        UserGUI.frame_count = UserGUI.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        print(fps)
        UserGUI.t0 = time.time()
        print(UserGUI.t0)
        UserGUI.valid = False
        try:
            resp = UserGUI.cap.read()
            UserGUI.shape = resp[1].shape
            UserGUI.valid = True
        except:
            UserGUI.shape = None
    
    
    def stop(UserGUI):
        if UserGUI.cap is not None:
            UserGUI.cap.release()
            print("Stop video")
    
    def get_frame(UserGUI):
        if UserGUI.valid:
            _,frame = UserGUI.cap.read()
            if frame is None:
                print("End of video")
                UserGUI.stop()
                print(time.time()-UserGUI.t0)
                return
            else:    
                frame = cv2.resize(frame,(640,480))
        else:
            frame = np.ones((480,640,3), dtype=np.uint8)
            col = (0,256,256)
            cv2.putText(frame, "(Error: Can not load the video)",
                       (65,220), cv2.FONT_HERSHEY_PLAIN, 2, col)
        return frame