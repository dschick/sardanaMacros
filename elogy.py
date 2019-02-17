##############################################################################
##
# This file is part of Sardana
##
# http://www.sardana-controls.org/
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Sardana is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Sardana is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

"""This is the elogy macro module"""

__all__ = []

__docformat__ = 'restructuredtext'

import json
import requests
import time
import datetime


import numpy as np
from taurus import Device
from taurus.console.table import Table
import PyTango
from PyTango import DevState

from sardana.macroserver.macro import Macro, macro, Type, ParamRepeat, \
    ViewOption, iMacro, Hookable
from sardana.macroserver.msexception import StopException
from sardana.macroserver.scan.scandata import Record
from sardana.macroserver.macro import Optional

################################ elogy client ##############################

class elogy_select_logbook(Macro):
    """ 
    """

    param_def = [
        ['logbookID', Type.Integer, 1, 'Logbook ID'],
        ['host', Type.String, 'http://localhost:4000', 'Elogy Host'],
    ]

    def run(self, logbookID, host):        
        # try accessing the host
        try:
            requests.get(host)
        except:
            self.error('Host: {} does not respond!'.format(host))
            return

        # try accessing the logbook
        try:
            url = '{}/api/logbooks/{}/'.format(host,logbookID)
            r = requests.get(url)
            status = r.status_code
        except:
            self.error('Logbook with ID {} does not exist!'.format(logbookID))
            return
        
        if status != 200:
            self.error('Logbook with ID {} does not exist!'.format(logbookID))
            return
        
        self.setEnv('ElogyHost', host)
        self.setEnv('ElogyLogbookID', logbookID)
        self.elogy_print_current_logbook()


class elogy_current_logbook(Macro):
    """
    """
    result_def = [['host', Type.String, None, 'Elogy Host'],
                  ['logbookID', Type.Integer, None, 'Logbook ID']]
    def run(self):
        try:
            host = self.getEnv('ElogyHost')
            logbookID = self.getEnv('ElogyLogbookID')
            return host, logbookID
        except:
            self.error('There is not elogy host or logbook selected.\n'
                       'Run %elogy_select_logbook')
            return None


class elogy_print_current_logbook(Macro):
    """
    """
    
    def run(self):
        ret = self.elogy_current_logbook()
        host, logbookID = ret.getResult()
        if (host == None) or (logbookID == None):
            return
        
        url = '{}/api/logbooks/{}/'.format(host,logbookID)
        r = requests.get(url)
        jdata = r.json()
        name = jdata['logbook']['name']
            
        self.output('Connected to elogy logbook\n\tID: {}\n\tName: {}\n\tHost: {}'.format(logbookID, name, host))
        

class elogy_post_entry(Macro):
    """
    """
    
    param_def = [
        ['authors', [
                ['login', Type.String, None, 'Author Login'],
                ['name',  Type.String, None, 'Author Name'],
                ['email', Type.String, None, 'Author Email'],
            ], None, 'Authors'],
        ['title', Type.String, None, 'Entry Title'],
        ['content', Type.String, None, 'Entry Content'],
        ['content_type', Type.String, 'text/html', 'Content Type'],
        ['follows', Type.Integer, Optional, 'ID of parent entry'],
    ]
    result_def = [['entryID', Type.Integer, None, 'Entry ID']]
    
    def run(self, authors, title, content, content_type, follows):
        ret = self.elogy_current_logbook()
        host, logbookID = ret.getResult()
        if (host == None) or (logbookID == None):
            return
        
        _authors = []
        for login, name, email in authors:
            _authors.append(dict(login=login, name=name, email=email))
        data = dict(
                title=title,
                content=content,
                authors=_authors,
                content_type=content_type,
                )
        if follows: # this is a followup
            url = '{}/api/logbooks/{}/entries/{}/'.format(host,logbookID, follows)
        else:
            url = '{}/api/logbooks/{}/entries/'.format(host,logbookID)
        r = requests.post(url, json=data)
        jdata = r.json()
        ID = jdata['entry']['id']
        self.setEnv('ElogyLastEntry', ID)
        return ID
        
        
class elogy_prescan(Macro):
    """       
    """
    
    def run(self):
        try:
            if self.getEnv('ElogyAutoscan') == False:
                return
        except:
            return
        
        parent = self.getParentMacro()
        if parent: # macro is called from another macro
            scan_id = self.getEnv('ScanID')
            motors = parent.motors
            starts = parent.starts
            finals = parent.finals
            name = parent.name
            if name == 'a1scan':
                name = 'ascan'
            elif name == 'd1scan':
                name = 'dscan'
            
            motor_str = ''
            for motor, start, final in zip(motors, starts, finals):
                motor_str += '{} {} {} '.format(motor.alias(), start, final)
            scan_cmd = '{} {}{} {} '.format(name, motor_str, parent.nr_interv, parent.integ_time)
            
            text = 'elogy_post_entry [["sardana" "Sardana XMCD" "sardana-xmcd@mbi-berlin.de"]] "scan #{}: {}" "Estimated time and PreScanSnapshot"'.format(scan_id, scan_cmd)
            ret = self.execMacro(text)
            ID = ret.getResult()
            self.setEnv('ElogyLastScanEntry', ID)
            self.info('New entry to elogy with ID {}: {}/logbooks/{}/entries/{}/'.format(ID, self.getEnv('ElogyHost'), self.getEnv('ElogyLogbookID'), ID))
        
class elogy_postscan(Macro):
    """       
    """
    
    def run(self):
        try:
            if self.getEnv('ElogyAutoscan') == False:
                return
        except:
            return
        
        parent = self.getParentMacro()
        if parent: # macro is called from another macro
            ScanHistory = self.getEnv('ScanHistory')
            output = ''
            for key, value in ScanHistory[-1].iteritems():
                output += '{} : {}<br/>'.format(key, value)
            
            cmd = ('elogy_post_entry [["sardana" "Sardana XMCD" "sardana-xmcd@mbi-berlin.de"]] '
                  '"Post Scan entry" "{}" '
                  '"text/html" {:d}'.format(output, self.getEnv('ElogyLastScanEntry')))
            ret = self.execMacro(cmd)
            ID = ret.getResult()
            self.setEnv('ElogyLastEntry', ID)


class elogy_enable_autoscan(Macro):
    """
    """
    
    def run(self):
        self.setEnv('ElogyAutoscan', True)

class elogy_disable_autoscan(Macro):
    """
    """
    
    def run(self):        
        self.setEnv('ElogyAutoscan', False)      


class elogy_wu(Macro):
    """       
    """
    
    def prepare(self):
        self.all_motors = self.findObjs('.*', type_class=Type.Moveable)
    
    def run(self):
        
        output = '<code>Current positions (user) on %s</code><br/><br/>' % datetime.datetime.now().isoformat(" ")
        
        self.table_opts = {}
        motor_list = self.all_motors
    
        motor_width = 9
        motor_names = []
        motor_pos = []
        motor_list = sorted(motor_list)
        pos_format = self.getViewOption(ViewOption.PosFormat)
        for motor in motor_list:
            name = motor.getName()
            motor_names.append([name])
            pos = motor.getPosition(force=True)
            if pos is None:
                pos = float('NAN')
            motor_pos.append((pos,))
            motor_width = max(motor_width, len(name))

        fmt = '%c*.%df' % ('%', motor_width - 5)
        if pos_format > -1:
            fmt = '%c*.%df' % ('%', int(pos_format))

        table = Table(motor_pos, elem_fmt=[fmt],
                      col_head_str=motor_names, col_head_width=motor_width,
                      **self.table_opts)
        for line in table.genOutput():
            output += '<code>' + line.replace(' ', '&nbsp;') + '</code><br/>'
        
        cmd = 'elogy_post_entry [["sardana" "Sardana XMCD" "sardana-xmcd@hhg.lab"]] "wu" "{}"'.format(output.encode('utf8'))
        self.execMacro(cmd)
        self.execMacro('wu')


class elogy_wa(Macro):
    """       
    """
    
    def prepare(self):
        self.all_motors = self.findObjs('.*', type_class=Type.Moveable)
    
    def run(self):
        output = '<code>Current positions (user, dial) on %s</code><br/><br/>' % datetime.datetime.now().isoformat(" ")
        
        self.table_opts = {}
        motor_list = self.all_motors
    
        show_dial = self.getViewOption(ViewOption.ShowDial)
        show_ctrlaxis = self.getViewOption(ViewOption.ShowCtrlAxis)
        pos_format = self.getViewOption(ViewOption.PosFormat)
        motor_width = 9
        motors = {}  # dict(motor name: motor obj)
        requests = {}  # dict(motor name: request id)
        data = {}  # dict(motor name: list of motor data)
        # sending asynchronous requests: neither Taurus nor Sardana extensions
        # allow asynchronous requests - use PyTango asynchronous request model
        for motor in motor_list:
            name = motor.getName()
            motors[name] = motor
            args = ('position',)
            if show_dial:
                args += ('dialposition',)
            _id = motor.read_attributes_asynch(args)
            requests[name] = _id
            motor_width = max(motor_width, len(name))
            data[name] = []
        # get additional motor information (ctrl name & axis)
        if show_ctrlaxis:
            for name, motor in motors.iteritems():
                ctrl_name = self.getController(motor.controller).name
                axis_nb = str(getattr(motor, "axis"))
                data[name].extend((ctrl_name, axis_nb))
                motor_width = max(motor_width, len(ctrl_name), len(axis_nb))
        # collect asynchronous replies
        while len(requests) > 0:
            req2delete = []
            for name, _id in requests.iteritems():
                motor = motors[name]
                try:
                    attrs = motor.read_attributes_reply(_id)
                    for attr in attrs:
                        value = attr.value
                        if value is None:
                            value = float('NaN')
                        data[name].append(value)
                    req2delete.append(name)
                except PyTango.AsynReplyNotArrived:
                    continue
                except PyTango.DevFailed:
                    data[name].append(float('NaN'))
                    if show_dial:
                        data[name].append(float('NaN'))
                    req2delete.append(name)
                    self.debug('Error when reading %s position(s)' % name)
                    self.debug('Details:', exc_info=1)
                    continue
            # removing motors which alredy replied
            for name in req2delete:
                requests.pop(name)
        # define format for numerical values
        fmt = '%c*.%df' % ('%', motor_width - 5)
        if pos_format > -1:
            fmt = '%c*.%df' % ('%', int(pos_format))
        # prepare row headers and formats
        row_headers = []
        t_format = []
        if show_ctrlaxis:
            row_headers += ['Ctrl', 'Axis']
            t_format += ['%*s', '%*s']
        row_headers.append('User')
        t_format.append(fmt)
        if show_dial:
            row_headers.append('Dial')
            t_format.append(fmt)
        # sort the data dict by keys
        col_headers = []
        values = []
        for mot_name, mot_values in sorted(data.items()):
            col_headers.append([mot_name])  # convert name to list
            values.append(mot_values)
        # create and print table
        table = Table(values, elem_fmt=t_format,
                      col_head_str=col_headers, col_head_width=motor_width,
                      row_head_str=row_headers)
        for line in table.genOutput():
            output += '<code>' + line.replace(' ', '&nbsp;') + '</code><br/>'
        
        cmd = 'elogy_post_entry [["sardana" "Sardana XMCD" "sardana-xmcd@hhg.lab"]] "wa" "{}"'.format(output.encode('utf8'))
        self.execMacro(cmd)
        self.execMacro('wa')