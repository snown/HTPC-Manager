#!/usr/bin/env python
# -*- coding: utf-8 -*-

import htpc
import cherrypy
import logging
from cherrypy.lib.auth2 import require
import paramiko
import xmltodict

# windows http://www.voidspace.org.uk/python/modules.shtml#pycrypto
# remember to update req.txt

class Vnstat(object):
    def __init__(self):
        self.logger = logging.getLogger("modules.vnstat")
        htpc.MODULES.append({
            "name": "Bandwidth",
            "id": "vnstat",
            "fields": [
                {"type": "bool", "label": "Enable", "name": "vnstat_enable"},
                {"type": "text", "label": "Menu name", "name": "vnstat_name"},
                {"type": "text", "label": "IP / Host", "placeholder": "localhost", "name": "vnstat_host"},
                {"type": "text", "label": "Username", "name": "vnstat_username"},
                {"type": "password", "label": "Password", "name": "vnstat_password"},

            ]
        })

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def index(self):
        pass

    @cherrypy.expose()
    @require()
    def run(self, cmd=''):
        if not cmd:
            return

        self.logger.debug('vnstat ssh %s' % cmd)

        hostname = htpc.settings.get('vnstat_host')
        username = htpc.settings.get('vnstat_username')
        password = htpc.settings.get('vnstat_password')

        client = paramiko.Transport((hostname, 22))
        client.connect(username=username, password=password)

        stdout_data = []
        stderr_data = []
        session = client.open_channel(kind='session')
        session.exec_command(cmd)
        while True:
            if session.recv_ready():
                stdout_data.append(session.recv(4096))
            if session.recv_stderr_ready():
                stderr_data.append(session.recv_stderr(4096))
            if session.exit_status_ready():
                break

        session.close()
        client.close()

        if session.recv_exit_status() == 1:
            self.logger.error("ssh failed")
            self.logger.error(''.join(stderr_data))
            #pass # some error 0 is ok 1

        # Make json of shitty xml
        if '--xml' in cmd:
            return xmltodict.parse(''.join(stdout_data))
        else:
            return ''.join(stdout_data)

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def day(self):
        return self.run('vnstat -d --xml')

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def live(self):
        # cant parse this. fix it
        r = self.run('vnstat -tr').strip()
        return r


    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def dump(self):
        return self.run('vnstat --dumpdb --xml')
