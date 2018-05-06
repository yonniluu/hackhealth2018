from lib.processors_noopenmdao import findFaceGetPulse
from lib.interface import plotXY, imshow, waitKey, destroyWindow
from cv2 import moveWindow
import cv2
import argparse
import numpy as np
import datetime
import socket
import sys
from subprocess import Popen, PIPE
import cv2
import struct
from video_listen import VideoCaptureYUV

class getPulse(object):

    def __init__(self):
        self.processor = findFaceGetPulse(bpm_limits = [50, 160],
                                          data_spike_limit = 2500.,
                                          face_detector_smoothness = 10.)
        self.bpm_plot = False
        self.plot_title = "Data display - raw signal (top) and PSD (bottom)"

        self.key_controls = {"s": self.toggle_search,
                             "d": self.toggle_display_plot,
                             "c": self.toggle_cam}
        # self.vidcap = cv2.VideoCapture(0)
        output = Popen(['./sdlexample',
                        '-a', '46113352',
                        '-s', '2_MX40NjExMzM1Mn5-MTUyNTU5MTQ1MzU1NX50Z0UxVHA4QzJRc3hldEtXdHN5NjJaN1V-fg',
                        '-t', 'T1==cGFydG5lcl9pZD00NjExMzM1MiZzaWc9ZGI1NjI5YjQxNmJjODc1NDdiM2FiZmZlM2Y3ZGMwYTM0M2Y4MzI4YTpzZXNzaW9uX2lkPTJfTVg0ME5qRXhNek0xTW41LU1UVXlOVFU1TVRRMU16VTFOWDUwWjBVeFZIQTRRekpSYzNobGRFdFhkSE41TmpKYU4xVi1mZyZjcmVhdGVfdGltZT0xNTI1NTk4OTQ0Jm5vbmNlPTAuMzQxMTcxNzM4Mzk0NDgzMiZyb2xlPXB1Ymxpc2hlciZleHBpcmVfdGltZT0xNTI1Njg1MzQ0JmNvbm5lY3Rpb25fZGF0YT1wYXRpZW50JmluaXRpYWxfbGF5b3V0X2NsYXNzX2xpc3Q9',
                        '-d', 'patient'
                        ], stdout = PIPE)
        size = (480, 640)
        self.vidcap = VideoCaptureYUV(output.stdout, size)

    def toggle_cam(self):
        self.processor.find_faces = True
        self.bpm_plot = False

    def toggle_search(self):
        """
        Toggles a motion lock on the processor's face detection component.

        Locking the forehead location in place significantly improves
        data quality, once a forehead has been sucessfully isolated.
        """
        # state = self.processor.find_faces.toggle()
        state = self.processor.find_faces_toggle()
        print("face detection lock =", not state)

    def toggle_display_plot(self):
        """
        Toggles the data display.
        """
        if self.bpm_plot:
            print("bpm plot disabled")
            self.bpm_plot = False
            destroyWindow(self.plot_title)
        else:
            print("bpm plot enabled")
            if self.processor.find_faces:
                self.toggle_search()
            self.bpm_plot = True
            self.make_bpm_plot()
            moveWindow(self.plot_title, self.w, 0)

    def make_bpm_plot(self):
        """
        Creates and/or updates the data display
        """
        plotXY([[self.processor.times,
                 self.processor.samples],
                [self.processor.freqs,
                 self.processor.fft]],
               labels = [False, True],
               showmax = [False, "bpm"],
               label_ndigits = [0, 0],
               showmax_digits = [0, 1],
               skip = [3, 3],
               name = self.plot_title,
               bg = self.processor.slices[0])

    def key_handler(self):
        """
        Handle keystrokes, as set at the bottom of __init__()

        A plotting or camera frame window must have focus for keypresses to be
        detected.
        """

        self.pressed = waitKey(10) & 255  # wait for keypress for 10 ms
        if self.pressed == 27:  # exit program on 'esc'
            print("Exiting")
            self.vidcap.release()
            cv2.destroyAllWindows()
            sys.exit()

        for key in self.key_controls.keys():
            if chr(self.pressed) == key:
                self.key_controls[key]()

    def main_loop(self):
        """
        Single iteration of the application's main loop.
        """
        # Get current image frame from the camera
        ret, frame = self.vidcap.read()
        #self.h, self.w, _c = frame.shape
        self.h, self.w, _c = (480, 640, 3)

        # set current image frame to the processor's input
        self.processor.frame_in = frame
        # process the image frame to perform all needed analysis
        self.processor.run(self.vidcap)
        # collect the output frame for display
        output_frame = self.processor.frame_out

        # show the processed/annotated output frame
        imshow("Processed", output_frame)

        # create and/or update the raw data display if needed
        if self.bpm_plot:
            self.make_bpm_plot()

        # handle any key presses
        self.key_handler()
if __name__ == "__main__":

    App = getPulse()
    while True:
        App.main_loop()

# cap = cv2.VideoCapture(0)
#
# while(True):
#     # Capture frame-by-frame
#     ret, frame = cap.read()
#
#     # Our operations on the frame come here
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#
#     # Display the resulting frame
#     cv2.imshow('frame',gray)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# # When everything done, release the capture
# cap.release()
# cv2.destroyAllWindows()