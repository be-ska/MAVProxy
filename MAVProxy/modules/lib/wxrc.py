#!/usr/bin/env python3

"""
  MAVProxy RC GUI
"""
from MAVProxy.modules.lib import multiproc
import time
from enum import Enum


class PanelType(Enum):
    SERVO_OUT = (0, "Servo Out", "Servo")
    RC_IN = (1, "RC In", "RC")

    def __new__(cls, value, display_string, short_string):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.display_string = display_string
        obj.short_string = short_string
        return obj


class RCStatus():
    '''
    A RC input and Servo output GUI for MAVProxy.
    '''
    def __init__(self, panelType):
        self.panelType = panelType
        # Create Pipe to send attitude information from module to UI
        self.child_pipe_recv, self.parent_pipe_send = multiproc.Pipe()
        self.close_event = multiproc.Event()
        self.close_event.clear()
        self.child = multiproc.Process(target=self.child_task)
        self.child.start()

    def child_task(self):
        '''child process - this holds all the GUI elements'''
        # Import wx_processguard before wx_loader to fix macOS threading issue
        from MAVProxy.modules.lib import wx_processguard  # noqa: F401
        from MAVProxy.modules.lib.wx_loader import wx
        from MAVProxy.modules.lib.wxrc_ui import RCFrame

        # Create wx application
        app = wx.App(False)
        app.frame = RCFrame(panelType=self.panelType, child_pipe_recv=self.child_pipe_recv)
        app.frame.SetDoubleBuffered(True)
        app.frame.Show()
        app.MainLoop()
        self.close_event.set()   # indicate that the GUI has closed

    def close(self):
        '''Close the window.'''
        self.close_event.set()
        if self.is_alive():
            self.child.join(2)
            self.parent_pipe_send.close()
            self.child_pipe_recv.close()

    def is_alive(self):
        '''check if child is still going'''
        return self.child.is_alive()

    def processPacket(self, m):
        '''Send mavlink packet onwards to panel'''
        self.parent_pipe_send.send(m)


if __name__ == "__main__":
    # test the console
    from MAVProxy.modules.lib.wxrc_ui import PanelType
    multiproc.freeze_support()
    rc_gui = RCStatus(PanelType.RC_IN)
    while rc_gui.is_alive():
        print('test')
        time.sleep(0.5)
