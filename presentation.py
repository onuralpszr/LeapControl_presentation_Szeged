#!/usr/bin/env python
#
#  Created by Onualp SEZER on 28/07/2013.
#  Copyright (c) 2013 Thunderbirdtr.blogspot.com All rights reserved.
#

#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:

#  1. Redistributions of source code must retain the above copyright notice, this
#  list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.>

#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#  ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import time
import Leap, sys
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture
from Xlib import X, display, ext, XK


class Listener_desktop(Leap.Listener):

    debug=0
    screenx=0
    screeny=0
    scalex=1.0
    scaley=1.0
    offsety=20.
    claw=0
    switcher=0
    rotationlock=0L
    nframes=10 
    frames=list()
    prevframes=list()
    rootw=0

    def on_init(self, controller):
        import subprocess, re
        from time import sleep, clock

        displ=display.Display()
        s=displ.screen()
        Listener_desktop.screenx=s.width_in_pixels
        Listener_desktop.screeny=s.height_in_pixels
        Listener_desktop.screenxmm=s.width_in_mms
        Listener_desktop.screenymm=s.height_in_mms
        Listener_desktop.scalex=s.width_in_pixels/300
        Listener_desktop.scaley=s.height_in_pixels/300
        Listener_desktop.rootw=s.root
        Listener_desktop.display=displ

        print "Screen size is:",Listener_desktop.screenx,Listener_desktop.screeny

        if (Listener_desktop.debug == 1):
            f=open('output.txt','w')
            for ind in range(5): f.write(str(ind)+'\n')
            f.close()
        print 'Initializing Leap Motion...'
        time0=clock()
        while (not controller.frame(2*Listener_desktop.nframes).is_valid):
            if clock()-time0 > 5:
                print "Timeout waiting for valid frames from the Leap Motion."
                print "Something's not right. Make sure the Leap Motion is connected"
                print 'and the leapd daemon is running'
                sys.exit(1)
        for iframe in range(Listener_desktop.nframes):
            Listener_desktop.frames.append(controller.frame(iframe))
            Listener_desktop.prevframes.append(controller.frame(iframe+Listener_desktop.nframes))
        print "Frame buffer sizes:",len(Listener_desktop.frames),len(Listener_desktop.prevframes)
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def on_disconnect(self, controller):

        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):

        def flush_buffer():
            Listener_desktop.prevframes[0:Listener_desktop.nframes]=Listener_desktop.frames[0:Listener_desktop.nframes]

        import commands
        from subprocess import call
        from time import sleep

        debug = Listener_desktop.debug
        leftkey=Listener_desktop.display.keysym_to_keycode(XK.XK_Right)
        rightkey=Listener_desktop.display.keysym_to_keycode(XK.XK_Left)
        currentframe=controller.frame()

        nframes2=Listener_desktop.nframes-10 
        nframes=Listener_desktop.nframes

        Listener_desktop.prevframes.pop(0)
        Listener_desktop.prevframes.append(Listener_desktop.frames[0])
        Listener_desktop.frames.pop(0)
        Listener_desktop.frames.append(currentframe)

        numfingers=len(currentframe.hands[0].fingers)

        frame = controller.frame()
        if not frame.hands.is_empty:
            hand = frame.hands[0]
            fingers = hand.fingers
            if not fingers.is_empty:

                avg_pos = Leap.Vector()
                for finger in fingers:
                    avg_pos += finger.tip_position
                avg_pos /= len(fingers)

            normal = hand.palm_normal
            direction = hand.direction

            for gesture in frame.gestures():
                if gesture.type == Leap.Gesture.TYPE_CIRCLE:
                    circle = CircleGesture(gesture)

                    if circle.pointable.direction.angle_to(circle.normal) <= Leap.PI/4:
                        clockwiseness = "clockwise"
                        print "Next Slide"
                        ext.xtest.fake_input(Listener_desktop.display, X.ButtonPress, 5)
                        ext.xtest.fake_input(Listener_desktop.display, X.ButtonRelease, 5)
                        Listener_desktop.display.flush()
                        Listener_desktop.display.flush()
                        flush_buffer()
                        Listener_desktop.rotationlock = currentframe.timestamp                        
                        time.sleep(1)
                        
                    else:
                        clockwiseness = "counterclockwise"
                        print "Previous Slide"
                        ext.xtest.fake_input(Listener_desktop.display, X.ButtonPress, 4)
                        ext.xtest.fake_input(Listener_desktop.display, X.ButtonRelease, 4)
                        Listener_desktop.display.flush()
                        flush_buffer()
                        Listener_desktop.rotationlock = currentframe.timestamp                        
                        time.sleep(1)
                        

                if gesture.type == Leap.Gesture.TYPE_SWIPE & gesture.id > 0 & gesture.type != Leap.Gesture.TYPE_CIRCLE:
                    swipe = SwipeGesture(gesture)
                    print "Swipe id: %d, state: %s, position: %s, direction: %s, speed: %f" % (
                            gesture.id, self.state_string(gesture.state),
                            swipe.position, swipe.direction, swipe.speed)
                    print ("Left to Right Swipe Gesture")
                    time.sleep(2)
                elif gesture.type == Leap.Gesture.TYPE_SWIPE & gesture.id < 0 & gesture.type != Leap.Gesture.TYPE_CIRCLE:
                    print("Right to Left Swipe Gesture")
                    time.sleep(2)

    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"




def main():

    listener = Listener_desktop()
    controller = Leap.Controller()

    controller.add_listener(listener)

    print "Press Enter to quit..."
    sys.stdin.readline()

    controller.remove_listener(listener)

if __name__ == "__main__":
    main()
