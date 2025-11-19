#!/usr/bin/env python3
'''
param editor module
Akshath Singhal
June 2019
'''

from MAVProxy.modules.lib import mp_module


class ParamEditorModule(mp_module.MPModule):
    '''
    A Graphical parameter editor for use with MAVProxy
    '''
    def __init__(self, mpstate):
        super(ParamEditorModule, self).__init__(mpstate,
                                                "paramedit", "param edit",
                                                public=True)

        # Create ParamEditorMain immediately to avoid file descriptor issues
        from MAVProxy.modules.mavproxy_paramedit import param_editor
        self.pe_main = param_editor.ParamEditorMain(self.mpstate)
        self.mpstate = mpstate

    def unload(self):
        '''unload module'''
        if self.pe_main:
            self.pe_main.unload()

    def idle_task(self):
        if self.pe_main:
            if self.pe_main.needs_unloading:
                self.needs_unloading = True
            self.pe_main.idle_task()

    def mavlink_packet(self, m):
        if self.pe_main:
            self.pe_main.mavlink_packet(m)


def init(mpstate):
    '''initialise module'''
    return ParamEditorModule(mpstate)
