import cv2
import numpy as np
import time
from face_detection import FaceDetection
from scipy import signal
# from sklearn.decomposition import FastICA

class Compute(object):
    def __init__(UserGUI):
        UserGUI.frame_in = np.zeros((10, 10, 3), np.uint8)
        UserGUI.frame_ROI = np.zeros((10, 10, 3), np.uint8)
        UserGUI.frame_out = np.zeros((10, 10, 3), np.uint8)
        UserGUI.samples = []
        UserGUI.buffer_size =120
        UserGUI.times = [] 
        UserGUI.data_buffer = []
        UserGUI.fps = 0
        UserGUI.fft = []
        UserGUI.freqs = []
        UserGUI.t0 = time.time()
        UserGUI.bpm = 0
        UserGUI.fd = FaceDetection()
        UserGUI.bpms = []
        UserGUI.peaks = []
        #UserGUI.red = np.zeros((256,256,3),np.uint8)
        
    def extractColor(UserGUI, frame):
        
        #r = np.mean(frame[:,:,0])
        g = np.mean(frame[:,:,1])
        #b = np.mean(frame[:,:,2])
        #return r, g, b
        return g           
    

        
    def run(UserGUI):
        
        frame, face_frame, ROI1, ROI2, ROI3, status, mask = UserGUI.fd.face_detect(UserGUI.frame_in)
        
        UserGUI.frame_out = frame
        UserGUI.frame_ROI = face_frame
        
        g1 = UserGUI.extractColor(ROI1)
        g2 = UserGUI.extractColor(ROI2)
        g3 = UserGUI.extractColor(ROI3)
        
        L = len(UserGUI.data_buffer)
        
        #calculate average green value of 2 ROIs
        #r = (r1+r2)/2
        #g = (g1+g2)/2
        g = g1
        #b = (b1+b2)/2
        
        
        if(abs(g-np.mean(UserGUI.data_buffer))>10 and L>119): #remove sudden change, if the avg value change is over 10, use the mean of the data_buffer
            g = UserGUI.data_buffer[-1]
        
        UserGUI.times.append(time.time() - UserGUI.t0)
        UserGUI.data_buffer.append(g)

        
        #only process in a fixed-size buffer
        if L > UserGUI.buffer_size:
            UserGUI.data_buffer = UserGUI.data_buffer[-UserGUI.buffer_size:]
            UserGUI.times = UserGUI.times[-UserGUI.buffer_size:]
            UserGUI.bpms = UserGUI.bpms[-UserGUI.buffer_size//2:]
            L = UserGUI.buffer_size
            
        processed = np.array(UserGUI.data_buffer)
        
        # start calculating after the first 10 frames
        if L == UserGUI.buffer_size:
            
            UserGUI.fps = float(L) / (UserGUI.times[-1] - UserGUI.times[0])#calculate HR using a true fps of processor of the computer, not the fps the camera provide
            even_times = np.linspace(UserGUI.times[0], UserGUI.times[-1], L)
            
            #processed = signal.detrend(processed)#detrend the signal to avoid interference of light change
            interpolated = np.interp(even_times, UserGUI.times, processed) #interpolation by 1
            interpolated = np.hamming(L) * interpolated#make the signal become more periodic (advoid spectral leakage)
            #norm = (interpolated - np.mean(interpolated))/np.std(interpolated)#normalization
            norm = interpolated/np.linalg.norm(interpolated)
            raw = np.fft.rfft(norm*30)#do real fft with the normalization multiplied by 10
            
            UserGUI.freqs = float(UserGUI.fps) / L * np.arange(L / 2 + 1)
            freqs = 60. * UserGUI.freqs
            
            # idx_remove = np.where((freqs < 50) & (freqs > 180))
            # raw[idx_remove] = 0
            
            UserGUI.fft = np.abs(raw)**2#get amplitude spectrum
        
            idx = np.where((freqs > 65) & (freqs < 120))#the range of frequency that HR is supposed to be within 
            pruned = UserGUI.fft[idx]
            pfreq = freqs[idx]
            
            UserGUI.freqs = pfreq 
            UserGUI.fft = pruned
            
            idx2 = np.argmax(pruned)#max in the range can be HR
            
            UserGUI.bpm = UserGUI.freqs[idx2]
            UserGUI.bpms.append(UserGUI.bpm)
            
            
            processed = UserGUI.butter_bandpass_filter(processed,0.8,3,UserGUI.fps,order = 3)
            #ifft = np.fft.irfft(raw)
        UserGUI.samples = processed # multiply the signal with 5 for easier to see in the plot
        #TODO: find peaks to draw HR-like signal.
        
        if(mask.shape[0]!=10): 
            out = np.zeros_like(face_frame)
            mask = mask.astype(np.bool)
            out[mask] = face_frame[mask]
            if(processed[-1]>np.mean(processed)):
                out[mask,2] = 180 + processed[-1]*10
            face_frame[mask] = out[mask]
            
            
        #cv2.imshow("face", face_frame)
        #out = cv2.add(face_frame,out)
        # else:
            # cv2.imshow("face", face_frame)
    
    def reset(UserGUI):
        UserGUI.frame_in = np.zeros((10, 10, 3), np.uint8)
        UserGUI.frame_ROI = np.zeros((10, 10, 3), np.uint8)
        UserGUI.frame_out = np.zeros((10, 10, 3), np.uint8)
        UserGUI.samples = []
        UserGUI.times = [] 
        UserGUI.data_buffer = []
        UserGUI.fps = 0
        UserGUI.fft = []
        UserGUI.freqs = []
        UserGUI.t0 = time.time()
        UserGUI.bpm = 0
        UserGUI.bpms = []
        
    def butter_bandpass(UserGUI, lowcut, highcut, fs, order=5):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = signal.butter(order, [low, high], btype='band')
        return b, a


    def butter_bandpass_filter(UserGUI, data, lowcut, highcut, fs, order=5):
        b, a = UserGUI.butter_bandpass(lowcut, highcut, fs, order=order)
        y = signal.lfilter(b, a, data)
        return y