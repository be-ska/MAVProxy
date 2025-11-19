#!/usr/bin/env python3

"""
  MAVProxy RC GUI - UI Components
"""
from MAVProxy.modules.lib.wx_loader import wx
import wx.lib.agw.pygauge as PG
import wx.lib.scrolledpanel
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


class RCPanel(wx.lib.scrolledpanel.ScrolledPanel):
    def __init__(self, parent, panelType=PanelType.RC_IN):
        super().__init__(parent)

        self.rc_labels = []
        self.rc_gauges = []
        self.rc_sizers = []

        self.panelType = panelType

        self.sizer_main = wx.BoxSizer(wx.VERTICAL)
        if self.panelType == PanelType.RC_IN:
            self.create_rc_widgets(18)
        else:
            self.create_rc_widgets(16)
        self.SetSizer(self.sizer_main)
        self.SetupScrolling()

    def create_rc_widgets(self, num_channels, starting_id=0):
        for i in range(num_channels):
            curChanSizer = wx.BoxSizer(wx.HORIZONTAL)
            label = wx.StaticText(self, label="{0} Channel {1}:".format(str(self.panelType.short_string),
                                                                        str(i+1+starting_id)))
            gauge = PG.PyGauge(self, range=2000, size=(200, 25), style=wx.GA_HORIZONTAL)  # Assuming RC values range from 1000 to 2000
            gauge.SetDrawValue(draw=True, drawPercent=False, font=None, colour=wx.BLACK, formatString=None)
            gauge.SetBarColour(wx.GREEN)
            gauge.SetBackgroundColour(wx.WHITE)
            gauge.SetBorderColor(wx.BLACK)
            gauge.SetValue(0)
            self.sizer_main.Add(curChanSizer, 1, wx.EXPAND, 0)
            self.rc_labels.append(label)
            self.rc_gauges.append(gauge)
            curChanSizer.Add(label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
            curChanSizer.Add(gauge, 1, wx.ALL | wx.EXPAND, 5)
            self.rc_sizers.append(curChanSizer)

    def update_gauges(self, msg):
        # Update the gauges based on the relevant mavlink packet info
        # Returns 1 if the window needs to be resized to fit additional gauges

        # If the vehicle is using >16 servo_outs, need to update the GUI
        if len(self.rc_gauges) == 16 and self.panelType == PanelType.SERVO_OUT and getattr(msg, 'port', 0) == 1:
            # add another 16 gauges
            self.create_rc_widgets(16, starting_id=16)
            self.Layout()
            self.SetupScrolling()
            return 1
        for i, gauge in enumerate(self.rc_gauges):
            if msg.get_type() == 'RC_CHANNELS' and self.panelType == PanelType.RC_IN:
                value = getattr(msg, 'chan{0}_raw'.format(i+1), 0)
                if value > gauge.GetRange():
                    gauge.SetRange(value + 50)
                gauge.SetValue(value)
                gauge.Refresh()
            elif (msg.get_type() == 'SERVO_OUTPUT_RAW' and self.panelType == PanelType.SERVO_OUT and
                  getattr(msg, 'port', 0) == 0) and i < 16:
                value = getattr(msg, 'servo{0}_raw'.format(i+1), 0)
                if value > gauge.GetRange():
                    gauge.SetRange(value + 50)
                gauge.SetValue(value)
                gauge.Refresh()
            elif (msg.get_type() == 'SERVO_OUTPUT_RAW' and self.panelType == PanelType.SERVO_OUT and
                  getattr(msg, 'port', 0) == 1) and i >= 17:
                # 2nd bank of servos (17-32), if used
                value = getattr(msg, 'servo{0}_raw'.format(i+1-16), 0)
                if value > gauge.GetRange():
                    gauge.SetRange(value + 50)
                gauge.SetValue(value)
                gauge.Refresh()
        return 0


class RCFrame(wx.Frame):
    def __init__(self, panelType, child_pipe_recv):
        super().__init__(None, title=panelType.display_string)
        self.panel = RCPanel(self, panelType)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.panel.sizer_main.Fit(self)
        # self.Center()
        self.Layout()

        self.child_pipe_recv = child_pipe_recv

        # Start a separate timer to update RC data
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(100)

    def on_timer(self, event):
        '''Main Loop.'''
        while self.child_pipe_recv.poll():
            msg = self.child_pipe_recv.recv()
            if msg:
                if self.panel.update_gauges(msg) == 1:
                    self.SetSize(self.GetSize()[0] + 30, self.GetSize()[1])

    def on_close(self, event):
        self.Destroy()
