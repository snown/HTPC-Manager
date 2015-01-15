#!/usr/bin/env python
# -*- coding: utf-8 -*-

import htpc
import cherrypy
import logging
from cherrypy.lib.auth2 import require
import xmltodict
import platform
import subprocess
import re

try:
    import paramiko
    importParamiko = True

except ImportError:
    importParamiko = False


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
                {"type": "bool", "label": "Use SSH?", 'desc': 'Used if vnstat is running on a different computer', "name": "vnstat_use_ssh"},
                {"type": "text", "label": "Vnstat DB location", "placeholder": "", "name": "vnstat_db"},
                {"type": "text", "label": "IP / Host", "placeholder": "localhost", "name": "vnstat_host"},
                {"type": "text", "label": "port", "name": "vnstat_port"},
                {"type": "text", "label": "Username", "name": "vnstat_username"},
                {"type": "password", "label": "Password", "name": "vnstat_password"},

            ]
        })

    @cherrypy.expose()
    @require()
    def index(self):
        return htpc.LOOKUP.get_template('vnstat.html').render(scriptname='vnstat', importParamiko=importParamiko)

    @cherrypy.expose()
    @require()
    def run(self, parameters=''):
        if htpc.settings.get('vnstat_enable'):
            hostname = htpc.settings.get('vnstat_host', '')
            port = htpc.settings.get('vnstat_port', 22)
            username = htpc.settings.get('vnstat_username', '')
            password = htpc.settings.get('vnstat_password', '')

            # If db saves the shit as a string
            if port:
                port = int(port)

            if not parameters:
                return

            if htpc.settings.get('vnstat_db', ''):
                cmd = "vnstat --dbdir %s %s" % (htpc.settings.get('vnstat_db', ''), parameters)
            else:
                cmd = "vnstat %s" % parameters

            # Force windows users to use paramiko as here isnt any native ssh.
            if htpc.settings.get('vnstat_use_ssh') or platform.system() == 'win32':
                client = paramiko.Transport((hostname, port))
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

            """
            else:
                # vnstat is running on the same computer as htpc manager
                self.logger.debug('Pipeing %s from shell' % cmd)
                s = ""
                if hostname and port:
                    s = "%s %s" % (hostname, port)
                if username and password:
                    s += "%s@%s" % (username, password)

                fullcmd = "ssh %s %s" (s, cmd)
                print fullcmd
                proc = subprocess.Popen(fullcmd, stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT, shell=True, cwd=htpc.RUNDIR)
                output, err = proc.communicate()
                returncode = proc.returncode

                if output and returncode == 0:
                    if '--xml' in cmd:
                        return xmltodict.parse(output.strip())
                    else:
                        return output.strip()
            """

    # Add a dropdown where users can choose parameter in dropdown?
    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def days(self):
        return self.run('-d --xml')

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def hours(self):
        return self.run('-h --xml')

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def exportdb(self):
        return self.run('--exportdb')

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def oneline(self):
        return self.run('--oneline')

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def cleartop(self):
        return self.run('--cleartop')

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def weeks(self):
        return self.run('-w --xml')

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def tr(self):
        piped = self.run('-tr')
        download = re.compile(ur'rx\s+(\d+.\d+)\s+(\w+\/s)')
        upload = re.compile(ur'tx\s+(\d+.\d+)\s+(\w+\/s)')
        rx = re.search(download, piped)
        tx = re.search(upload, piped)
        if rx:
            rx = '%s %s' % (rx.group(1), rx.group(2))
        if tx:
            tx = '%s %s' % (tx.group(1), tx.group(2))

        return {'rx': rx, 'tx': tx}

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def top10(self):
        return self.run('-t --xml')

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def dumpdb(self):
        return self.run('--dumpdb --xml')

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def dump2(self):
        z = '''<vnstat version="1.11" xmlversion="1">
            <interface id="em0">
                <id>em0</id>
                <nick>em0</nick>
                <created><date><year>2014</year><month>01</month><day>27</day></date></created>
              <updated><date><year>2015</year><month>01</month><day>10</day></date><time><hour>09</hour><minute>32</minute></time></updated>
              <traffic>
               <total><rx>12317957812</rx><tx>1593377266</tx></total>
               <days>
                <day id="0"><date><year>2015</year><month>01</month><day>10</day></date><rx>1369116</rx><tx>215127</tx></day>
                <day id="1"><date><year>2015</year><month>01</month><day>09</day></date><rx>21647407</rx><tx>1380558</tx></day>
                <day id="2"><date><year>2015</year><month>01</month><day>08</day></date><rx>8857005</rx><tx>3197637</tx></day>
                <day id="3"><date><year>2015</year><month>01</month><day>07</day></date><rx>10166444</rx><tx>2023108</tx></day>
                <day id="4"><date><year>2015</year><month>01</month><day>06</day></date><rx>22528099</rx><tx>2230285</tx></day>
                <day id="5"><date><year>2015</year><month>01</month><day>05</day></date><rx>8429231</rx><tx>1526782</tx></day>
                <day id="6"><date><year>2015</year><month>01</month><day>04</day></date><rx>22500120</rx><tx>3086997</tx></day>
                <day id="7"><date><year>2015</year><month>01</month><day>03</day></date><rx>15653968</rx><tx>4099809</tx></day>
                <day id="8"><date><year>2015</year><month>01</month><day>02</day></date><rx>73975504</rx><tx>3304843</tx></day>
                <day id="9"><date><year>2015</year><month>01</month><day>01</day></date><rx>20030280</rx><tx>5498150</tx></day>
                <day id="10"><date><year>2014</year><month>12</month><day>31</day></date><rx>16176549</rx><tx>1779845</tx></day>
                <day id="11"><date><year>2014</year><month>12</month><day>30</day></date><rx>23259265</rx><tx>2235905</tx></day>
                <day id="12"><date><year>2014</year><month>12</month><day>29</day></date><rx>24526936</rx><tx>2620146</tx></day>
                <day id="13"><date><year>2014</year><month>12</month><day>28</day></date><rx>79575725</rx><tx>3173981</tx></day>
                <day id="14"><date><year>2014</year><month>12</month><day>27</day></date><rx>25801096</rx><tx>1707097</tx></day>
                <day id="15"><date><year>2014</year><month>12</month><day>26</day></date><rx>18056569</rx><tx>921144</tx></day>
                <day id="16"><date><year>2014</year><month>12</month><day>25</day></date><rx>4737477</rx><tx>930725</tx></day>
                <day id="17"><date><year>2014</year><month>12</month><day>24</day></date><rx>2106823</rx><tx>568021</tx></day>
                <day id="18"><date><year>2014</year><month>12</month><day>23</day></date><rx>11502505</rx><tx>972777</tx></day>
                <day id="19"><date><year>2014</year><month>12</month><day>22</day></date><rx>24434307</rx><tx>1647779</tx></day>
                <day id="20"><date><year>2014</year><month>12</month><day>21</day></date><rx>5619597</rx><tx>1853425</tx></day>
                <day id="21"><date><year>2014</year><month>12</month><day>20</day></date><rx>16445618</rx><tx>1596675</tx></day>
                <day id="22"><date><year>2014</year><month>12</month><day>19</day></date><rx>12068921</rx><tx>1946027</tx></day>
                <day id="23"><date><year>2014</year><month>12</month><day>18</day></date><rx>10072440</rx><tx>1327896</tx></day>
                <day id="24"><date><year>2014</year><month>12</month><day>17</day></date><rx>29541634</rx><tx>1908814</tx></day>
                <day id="25"><date><year>2014</year><month>12</month><day>16</day></date><rx>7086506</rx><tx>2034646</tx></day>
                <day id="26"><date><year>2014</year><month>12</month><day>15</day></date><rx>28123665</rx><tx>2235844</tx></day>
                <day id="27"><date><year>2014</year><month>12</month><day>14</day></date><rx>10600522</rx><tx>2172581</tx></day>
                <day id="28"><date><year>2014</year><month>12</month><day>13</day></date><rx>4619159</rx><tx>3594093</tx></day>
                <day id="29"><date><year>2014</year><month>12</month><day>12</day></date><rx>4125866</rx><tx>1730222</tx></day>
               </days>
               <months>
                <month id="0"><date><year>2015</year><month>01</month></date><rx>205157174</rx><tx>26563296</tx></month>
                <month id="1"><date><year>2014</year><month>12</month></date><rx>988423612</rx><tx>63854422</tx></month>
                <month id="2"><date><year>2014</year><month>11</month></date><rx>722362506</rx><tx>59351824</tx></month>
                <month id="3"><date><year>2014</year><month>10</month></date><rx>557736460</rx><tx>67193717</tx></month>
                <month id="4"><date><year>2014</year><month>09</month></date><rx>542074802</rx><tx>74616209</tx></month>
                <month id="5"><date><year>2014</year><month>08</month></date><rx>471970533</rx><tx>100063645</tx></month>
                <month id="6"><date><year>2014</year><month>07</month></date><rx>3708214135</rx><tx>142401988</tx></month>
                <month id="7"><date><year>2014</year><month>06</month></date><rx>1417761098</rx><tx>132461875</tx></month>
                <month id="8"><date><year>2014</year><month>05</month></date><rx>962234750</rx><tx>105519915</tx></month>
                <month id="9"><date><year>2014</year><month>04</month></date><rx>829111993</rx><tx>239267272</tx></month>
                <month id="10"><date><year>2014</year><month>03</month></date><rx>846856483</rx><tx>181512576</tx></month>
                <month id="11"><date><year>2014</year><month>02</month></date><rx>765951981</rx><tx>369852894</tx></month>
               </months>
               <tops>
                <top id="0"><date><year>2014</year><month>07</month><day>29</day></date><time><hour>00</hour><minute>00</minute></time><rx>406428223</rx><tx>11627349</tx></top>
                <top id="1"><date><year>2014</year><month>07</month><day>14</day></date><time><hour>00</hour><minute>00</minute></time><rx>254596437</rx><tx>8738789</tx></top>
                <top id="2"><date><year>2014</year><month>07</month><day>13</day></date><time><hour>00</hour><minute>00</minute></time><rx>236599199</rx><tx>8627912</tx></top>
                <top id="3"><date><year>2014</year><month>07</month><day>02</day></date><time><hour>00</hour><minute>00</minute></time><rx>237474154</rx><tx>6898986</tx></top>
                <top id="4"><date><year>2014</year><month>07</month><day>28</day></date><time><hour>00</hour><minute>00</minute></time><rx>233660835</rx><tx>9053283</tx></top>
                <top id="5"><date><year>2014</year><month>07</month><day>06</day></date><time><hour>00</hour><minute>00</minute></time><rx>223820176</rx><tx>10443523</tx></top>
                <top id="6"><date><year>2014</year><month>07</month><day>16</day></date><time><hour>00</hour><minute>00</minute></time><rx>225270600</rx><tx>7260756</tx></top>
                <top id="7"><date><year>2014</year><month>07</month><day>07</day></date><time><hour>00</hour><minute>00</minute></time><rx>211347181</rx><tx>6998310</tx></top>
                <top id="8"><date><year>2014</year><month>07</month><day>03</day></date><time><hour>00</hour><minute>00</minute></time><rx>200105719</rx><tx>8743853</tx></top>
                <top id="9"><date><year>2014</year><month>07</month><day>05</day></date><time><hour>00</hour><minute>00</minute></time><rx>199219505</rx><tx>7317852</tx></top>
               </tops>
               <hours>
                <hour id="0"><date><year>2015</year><month>01</month><day>10</day></date><rx>19484</rx><tx>92787</tx></hour>
                <hour id="1"><date><year>2015</year><month>01</month><day>10</day></date><rx>7711</rx><tx>1324</tx></hour>
                <hour id="2"><date><year>2015</year><month>01</month><day>10</day></date><rx>5473</rx><tx>1094</tx></hour>
                <hour id="3"><date><year>2015</year><month>01</month><day>10</day></date><rx>5115</rx><tx>994</tx></hour>
                <hour id="4"><date><year>2015</year><month>01</month><day>10</day></date><rx>5327</rx><tx>977</tx></hour>
                <hour id="5"><date><year>2015</year><month>01</month><day>10</day></date><rx>5342</rx><tx>1033</tx></hour>
                <hour id="6"><date><year>2015</year><month>01</month><day>10</day></date><rx>5384</rx><tx>1044</tx></hour>
                <hour id="7"><date><year>2015</year><month>01</month><day>10</day></date><rx>6589</rx><tx>12899</tx></hour>
                <hour id="8"><date><year>2015</year><month>01</month><day>10</day></date><rx>999542</rx><tx>90780</tx></hour>
                <hour id="9"><date><year>2015</year><month>01</month><day>10</day></date><rx>309149</rx><tx>12195</tx></hour>
                <hour id="10"><date><year>2015</year><month>01</month><day>09</day></date><rx>678860</rx><tx>12620</tx></hour>
                <hour id="11"><date><year>2015</year><month>01</month><day>09</day></date><rx>407172</rx><tx>21991</tx></hour>
                <hour id="12"><date><year>2015</year><month>01</month><day>09</day></date><rx>846278</rx><tx>43883</tx></hour>
                <hour id="13"><date><year>2015</year><month>01</month><day>09</day></date><rx>4676</rx><tx>922</tx></hour>
                <hour id="14"><date><year>2015</year><month>01</month><day>09</day></date><rx>8589</rx><tx>1143</tx></hour>
                <hour id="15"><date><year>2015</year><month>01</month><day>09</day></date><rx>72903</rx><tx>11045</tx></hour>
                <hour id="16"><date><year>2015</year><month>01</month><day>09</day></date><rx>231693</rx><tx>19314</tx></hour>
                <hour id="17"><date><year>2015</year><month>01</month><day>09</day></date><rx>52218</rx><tx>11293</tx></hour>
                <hour id="18"><date><year>2015</year><month>01</month><day>09</day></date><rx>160355</rx><tx>153472</tx></hour>
                <hour id="19"><date><year>2015</year><month>01</month><day>09</day></date><rx>2954212</rx><tx>207744</tx></hour>
                <hour id="20"><date><year>2015</year><month>01</month><day>09</day></date><rx>282861</rx><tx>212808</tx></hour>
                <hour id="21"><date><year>2015</year><month>01</month><day>09</day></date><rx>2461983</rx><tx>83084</tx></hour>
                <hour id="22"><date><year>2015</year><month>01</month><day>09</day></date><rx>10410273</rx><tx>414657</tx></hour>
                <hour id="23"><date><year>2015</year><month>01</month><day>09</day></date><rx>18129</rx><tx>73884</tx></hour>
               </hours>
              </traffic>
             </interface>
            </vnstat> '''
        return xmltodict.parse(z)
        #return self.run('vnstat --dumpdb --xml')

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def dump3(self):
        z = '''<vnstat version="1.11" xmlversion="1">
             <interface id="eth1">
              <id>eth1</id>
              <nick>eth1</nick>
              <created><date><year>2015</year><month>01</month><day>04</day></date></created>
              <updated><date><year>2015</year><month>01</month><day>11</day></date><time><hour>11</hour><minute>13</minute></time></updated>
              <traffic>
               <total><rx>63351406</rx><tx>4471677</tx></total>
               <days>
                <day id="0"><date><year>2015</year><month>01</month><day>11</day></date><rx>84222</rx><tx>13457</tx></day>
                <day id="1"><date><year>2015</year><month>01</month><day>10</day></date><rx>5465114</rx><tx>779592</tx></day>
                <day id="2"><date><year>2015</year><month>01</month><day>09</day></date><rx>1953705</rx><tx>79419</tx></day>
                <day id="3"><date><year>2015</year><month>01</month><day>08</day></date><rx>6392783</rx><tx>216039</tx></day>
                <day id="4"><date><year>2015</year><month>01</month><day>07</day></date><rx>67614</rx><tx>19253</tx></day>
                <day id="5"><date><year>2015</year><month>01</month><day>06</day></date><rx>122136</rx><tx>13085</tx></day>
                <day id="6"><date><year>2015</year><month>01</month><day>05</day></date><rx>25560303</rx><tx>2654726</tx></day>
                <day id="7"><date><year>2015</year><month>01</month><day>04</day></date><rx>23705529</rx><tx>696106</tx></day>
               </days>
               <months>
                <month id="0"><date><year>2015</year><month>01</month></date><rx>63351406</rx><tx>4471677</tx></month>
               </months>
               <tops>
                <top id="0"><date><year>2015</year><month>01</month><day>05</day></date><time><hour>00</hour><minute>00</minute></time><rx>25560303</rx><tx>2654726</tx></top>
                <top id="1"><date><year>2015</year><month>01</month><day>04</day></date><time><hour>21</hour><minute>00</minute></time><rx>23705529</rx><tx>696106</tx></top>
                <top id="2"><date><year>2015</year><month>01</month><day>08</day></date><time><hour>00</hour><minute>00</minute></time><rx>6392783</rx><tx>216039</tx></top>
                <top id="3"><date><year>2015</year><month>01</month><day>10</day></date><time><hour>00</hour><minute>00</minute></time><rx>5465114</rx><tx>779592</tx></top>
                <top id="4"><date><year>2015</year><month>01</month><day>09</day></date><time><hour>00</hour><minute>00</minute></time><rx>1953705</rx><tx>79419</tx></top>
                <top id="5"><date><year>2015</year><month>01</month><day>06</day></date><time><hour>00</hour><minute>00</minute></time><rx>122136</rx><tx>13085</tx></top>
                <top id="6"><date><year>2015</year><month>01</month><day>07</day></date><time><hour>00</hour><minute>00</minute></time><rx>67614</rx><tx>19253</tx></top>
               </tops>
               <hours>
                <hour id="0"><date><year>2015</year><month>01</month><day>11</day></date><rx>11584</rx><tx>709</tx></hour>
                <hour id="1"><date><year>2015</year><month>01</month><day>11</day></date><rx>2290</rx><tx>408</tx></hour>
                <hour id="2"><date><year>2015</year><month>01</month><day>11</day></date><rx>4467</rx><tx>977</tx></hour>
                <hour id="3"><date><year>2015</year><month>01</month><day>11</day></date><rx>8888</rx><tx>793</tx></hour>
                <hour id="4"><date><year>2015</year><month>01</month><day>11</day></date><rx>6459</rx><tx>674</tx></hour>
                <hour id="5"><date><year>2015</year><month>01</month><day>11</day></date><rx>1844</rx><tx>404</tx></hour>
                <hour id="6"><date><year>2015</year><month>01</month><day>11</day></date><rx>2672</rx><tx>509</tx></hour>
                <hour id="7"><date><year>2015</year><month>01</month><day>11</day></date><rx>1765</rx><tx>409</tx></hour>
                <hour id="8"><date><year>2015</year><month>01</month><day>11</day></date><rx>2342</rx><tx>415</tx></hour>
                <hour id="9"><date><year>2015</year><month>01</month><day>11</day></date><rx>7726</rx><tx>2399</tx></hour>
                <hour id="10"><date><year>2015</year><month>01</month><day>11</day></date><rx>33790</rx><tx>5673</tx></hour>
                <hour id="11"><date><year>2015</year><month>01</month><day>11</day></date><rx>395</rx><tx>87</tx></hour>
                <hour id="12"><date><year>2015</year><month>01</month><day>10</day></date><rx>3340</rx><tx>604</tx></hour>
                <hour id="13"><date><year>2015</year><month>01</month><day>10</day></date><rx>2509</rx><tx>517</tx></hour>
                <hour id="14"><date><year>2015</year><month>01</month><day>10</day></date><rx>10896</rx><tx>767</tx></hour>
                <hour id="15"><date><year>2015</year><month>01</month><day>10</day></date><rx>39645</rx><tx>1357</tx></hour>
                <hour id="16"><date><year>2015</year><month>01</month><day>10</day></date><rx>2474</rx><tx>499</tx></hour>
                <hour id="17"><date><year>2015</year><month>01</month><day>10</day></date><rx>2669</rx><tx>497</tx></hour>
                <hour id="18"><date><year>2015</year><month>01</month><day>10</day></date><rx>20592</rx><tx>1021</tx></hour>
                <hour id="19"><date><year>2015</year><month>01</month><day>10</day></date><rx>2437</rx><tx>484</tx></hour>
                <hour id="20"><date><year>2015</year><month>01</month><day>10</day></date><rx>10947</rx><tx>717</tx></hour>
                <hour id="21"><date><year>2015</year><month>01</month><day>10</day></date><rx>6979</rx><tx>741</tx></hour>
                <hour id="22"><date><year>2015</year><month>01</month><day>10</day></date><rx>2680</rx><tx>2131</tx></hour>
                <hour id="23"><date><year>2015</year><month>01</month><day>10</day></date><rx>2298</rx><tx>752</tx></hour>
               </hours>
              </traffic>
             </interface>
             <interface id="wlan0">
              <id>wlan0</id>
              <nick>wlan0</nick>
              <created><date><year>2015</year><month>01</month><day>04</day></date></created>
              <updated><date><year>2015</year><month>01</month><day>11</day></date><time><hour>11</hour><minute>13</minute></time></updated>
              <traffic>
               <total><rx>0</rx><tx>0</tx></total>
               <days>
                <day id="0"><date><year>2015</year><month>01</month><day>11</day></date><rx>0</rx><tx>0</tx></day>
                <day id="1"><date><year>2015</year><month>01</month><day>10</day></date><rx>0</rx><tx>0</tx></day>
                <day id="2"><date><year>2015</year><month>01</month><day>09</day></date><rx>0</rx><tx>0</tx></day>
                <day id="3"><date><year>2015</year><month>01</month><day>08</day></date><rx>0</rx><tx>0</tx></day>
                <day id="4"><date><year>2015</year><month>01</month><day>07</day></date><rx>0</rx><tx>0</tx></day>
                <day id="5"><date><year>2015</year><month>01</month><day>06</day></date><rx>0</rx><tx>0</tx></day>
                <day id="6"><date><year>2015</year><month>01</month><day>05</day></date><rx>0</rx><tx>0</tx></day>
                <day id="7"><date><year>2015</year><month>01</month><day>04</day></date><rx>0</rx><tx>0</tx></day>
               </days>
               <months>
                <month id="0"><date><year>2015</year><month>01</month></date><rx>0</rx><tx>0</tx></month>
               </months>
               <tops>
               </tops>
               <hours>
                <hour id="0"><date><year>2015</year><month>01</month><day>11</day></date><rx>0</rx><tx>0</tx></hour>
                <hour id="1"><date><year>2015</year><month>01</month><day>11</day></date><rx>0</rx><tx>0</tx></hour>
                <hour id="2"><date><year>2015</year><month>01</month><day>11</day></date><rx>0</rx><tx>0</tx></hour>
                <hour id="3"><date><year>2015</year><month>01</month><day>11</day></date><rx>0</rx><tx>0</tx></hour>
                <hour id="4"><date><year>2015</year><month>01</month><day>11</day></date><rx>0</rx><tx>0</tx></hour>
                <hour id="5"><date><year>2015</year><month>01</month><day>11</day></date><rx>0</rx><tx>0</tx></hour>
                <hour id="6"><date><year>2015</year><month>01</month><day>11</day></date><rx>0</rx><tx>0</tx></hour>
                <hour id="7"><date><year>2015</year><month>01</month><day>11</day></date><rx>0</rx><tx>0</tx></hour>
                <hour id="8"><date><year>2015</year><month>01</month><day>11</day></date><rx>0</rx><tx>0</tx></hour>
                <hour id="9"><date><year>2015</year><month>01</month><day>11</day></date><rx>0</rx><tx>0</tx></hour>
                <hour id="10"><date><year>2015</year><month>01</month><day>11</day></date><rx>0</rx><tx>0</tx></hour>
                <hour id="11"><date><year>2015</year><month>01</month><day>11</day></date><rx>0</rx><tx>0</tx></hour>
                <hour id="12"><date><year>2015</year><month>01</month><day>10</day></date><rx>0</rx><tx>0</tx></hour>
                <hour id="13"><date><year>2015</year><month>01</month><day>10</day></date><rx>0</rx><tx>0</tx></hour>
                <hour id="14"><date><year>2015</year><month>01</month><day>10</day></date><rx>0</rx><tx>0</tx></hour>
                <hour id="15"><date><year>2015</year><month>01</month><day>10</day></date><rx>0</rx><tx>0</tx></hour>
                <hour id="16"><date><year>2015</year><month>01</month><day>10</day></date><rx>0</rx><tx>0</tx></hour>
                <hour id="17"><date><year>2015</year><month>01</month><day>10</day></date><rx>0</rx><tx>0</tx></hour>
                <hour id="18"><date><year>2015</year><month>01</month><day>10</day></date><rx>0</rx><tx>0</tx></hour>
                <hour id="19"><date><year>2015</year><month>01</month><day>10</day></date><rx>0</rx><tx>0</tx></hour>
                <hour id="20"><date><year>2015</year><month>01</month><day>10</day></date><rx>0</rx><tx>0</tx></hour>
                <hour id="21"><date><year>2015</year><month>01</month><day>10</day></date><rx>0</rx><tx>0</tx></hour>
                <hour id="22"><date><year>2015</year><month>01</month><day>10</day></date><rx>0</rx><tx>0</tx></hour>
                <hour id="23"><date><year>2015</year><month>01</month><day>10</day></date><rx>0</rx><tx>0</tx></hour>
               </hours>
              </traffic>
             </interface>
             <interface id="eth0">
              <id>eth0</id>
              <nick>eth0</nick>
              <created><date><year>2015</year><month>01</month><day>04</day></date></created>
              <updated><date><year>2015</year><month>01</month><day>11</day></date><time><hour>11</hour><minute>13</minute></time></updated>
              <traffic>
               <total><rx>24960817</rx><tx>168924363</tx></total>
               <days>
                <day id="0"><date><year>2015</year><month>01</month><day>11</day></date><rx>102545</rx><tx>391591</tx></day>
                <day id="1"><date><year>2015</year><month>01</month><day>10</day></date><rx>3049337</rx><tx>12684843</tx></day>
                <day id="2"><date><year>2015</year><month>01</month><day>09</day></date><rx>4626924</rx><tx>30611307</tx></day>
                <day id="3"><date><year>2015</year><month>01</month><day>08</day></date><rx>5333653</rx><tx>21464631</tx></day>
                <day id="4"><date><year>2015</year><month>01</month><day>07</day></date><rx>4817343</rx><tx>24607274</tx></day>
                <day id="5"><date><year>2015</year><month>01</month><day>06</day></date><rx>3166670</rx><tx>19538181</tx></day>
                <day id="6"><date><year>2015</year><month>01</month><day>05</day></date><rx>3042200</rx><tx>48018228</tx></day>
                <day id="7"><date><year>2015</year><month>01</month><day>04</day></date><rx>822145</rx><tx>11608308</tx></day>
               </days>
               <months>
                <month id="0"><date><year>2015</year><month>01</month></date><rx>24960817</rx><tx>168924363</tx></month>
               </months>
               <tops>
                <top id="0"><date><year>2015</year><month>01</month><day>05</day></date><time><hour>00</hour><minute>00</minute></time><rx>3042200</rx><tx>48018228</tx></top>
                <top id="1"><date><year>2015</year><month>01</month><day>09</day></date><time><hour>00</hour><minute>00</minute></time><rx>4626924</rx><tx>30611307</tx></top>
                <top id="2"><date><year>2015</year><month>01</month><day>07</day></date><time><hour>00</hour><minute>00</minute></time><rx>4817343</rx><tx>24607274</tx></top>
                <top id="3"><date><year>2015</year><month>01</month><day>08</day></date><time><hour>00</hour><minute>00</minute></time><rx>5333653</rx><tx>21464631</tx></top>
                <top id="4"><date><year>2015</year><month>01</month><day>06</day></date><time><hour>00</hour><minute>00</minute></time><rx>3166670</rx><tx>19538181</tx></top>
                <top id="5"><date><year>2015</year><month>01</month><day>10</day></date><time><hour>00</hour><minute>00</minute></time><rx>3049337</rx><tx>12684843</tx></top>
                <top id="6"><date><year>2015</year><month>01</month><day>04</day></date><time><hour>21</hour><minute>00</minute></time><rx>822145</rx><tx>11608308</tx></top>
               </tops>
               <hours>
                <hour id="0"><date><year>2015</year><month>01</month><day>11</day></date><rx>5351</rx><tx>5182</tx></hour>
                <hour id="1"><date><year>2015</year><month>01</month><day>11</day></date><rx>5452</rx><tx>5303</tx></hour>
                <hour id="2"><date><year>2015</year><month>01</month><day>11</day></date><rx>5377</rx><tx>5150</tx></hour>
                <hour id="3"><date><year>2015</year><month>01</month><day>11</day></date><rx>5355</rx><tx>5223</tx></hour>
                <hour id="4"><date><year>2015</year><month>01</month><day>11</day></date><rx>5239</rx><tx>5131</tx></hour>
                <hour id="5"><date><year>2015</year><month>01</month><day>11</day></date><rx>5282</rx><tx>5103</tx></hour>
                <hour id="6"><date><year>2015</year><month>01</month><day>11</day></date><rx>5259</rx><tx>5091</tx></hour>
                <hour id="7"><date><year>2015</year><month>01</month><day>11</day></date><rx>5260</rx><tx>5089</tx></hour>
                <hour id="8"><date><year>2015</year><month>01</month><day>11</day></date><rx>5283</rx><tx>5176</tx></hour>
                <hour id="9"><date><year>2015</year><month>01</month><day>11</day></date><rx>44316</rx><tx>327533</tx></hour>
                <hour id="10"><date><year>2015</year><month>01</month><day>11</day></date><rx>8963</rx><tx>15389</tx></hour>
                <hour id="11"><date><year>2015</year><month>01</month><day>11</day></date><rx>1408</rx><tx>2221</tx></hour>
                <hour id="12"><date><year>2015</year><month>01</month><day>10</day></date><rx>501972</rx><tx>296194</tx></hour>
                <hour id="13"><date><year>2015</year><month>01</month><day>10</day></date><rx>117674</rx><tx>107272</tx></hour>
                <hour id="14"><date><year>2015</year><month>01</month><day>10</day></date><rx>61832</rx><tx>73586</tx></hour>
                <hour id="15"><date><year>2015</year><month>01</month><day>10</day></date><rx>5311</rx><tx>19726</tx></hour>
                <hour id="16"><date><year>2015</year><month>01</month><day>10</day></date><rx>5388</rx><tx>4878</tx></hour>
                <hour id="17"><date><year>2015</year><month>01</month><day>10</day></date><rx>34377</rx><tx>1178434</tx></hour>
                <hour id="18"><date><year>2015</year><month>01</month><day>10</day></date><rx>18096</rx><tx>495471</tx></hour>
                <hour id="19"><date><year>2015</year><month>01</month><day>10</day></date><rx>5862</rx><tx>5521</tx></hour>
                <hour id="20"><date><year>2015</year><month>01</month><day>10</day></date><rx>6852</rx><tx>11953</tx></hour>
                <hour id="21"><date><year>2015</year><month>01</month><day>10</day></date><rx>7388</rx><tx>15253</tx></hour>
                <hour id="22"><date><year>2015</year><month>01</month><day>10</day></date><rx>6072</rx><tx>5527</tx></hour>
                <hour id="23"><date><year>2015</year><month>01</month><day>10</day></date><rx>5434</rx><tx>5251</tx></hour>
               </hours>
              </traffic>
             </interface>
             <interface id="bond0">
              <id>bond0</id>
              <nick>bond0</nick>
              <created><date><year>2015</year><month>01</month><day>04</day></date></created>
              <updated><date><year>2015</year><month>01</month><day>11</day></date><time><hour>11</hour><minute>13</minute></time></updated>
              <traffic>
               <total><rx>88311907</rx><tx>173398135</tx></total>
               <days>
                <day id="0"><date><year>2015</year><month>01</month><day>11</day></date><rx>186766</rx><tx>405047</tx></day>
                <day id="1"><date><year>2015</year><month>01</month><day>10</day></date><rx>8514439</rx><tx>13464434</tx></day>
                <day id="2"><date><year>2015</year><month>01</month><day>09</day></date><rx>6580611</rx><tx>30690740</tx></day>
                <day id="3"><date><year>2015</year><month>01</month><day>08</day></date><rx>11726428</rx><tx>21680669</tx></day>
                <day id="4"><date><year>2015</year><month>01</month><day>07</day></date><rx>4884754</rx><tx>24626526</tx></day>
                <day id="5"><date><year>2015</year><month>01</month><day>06</day></date><rx>3288758</rx><tx>19551164</tx></day>
                <day id="6"><date><year>2015</year><month>01</month><day>05</day></date><rx>28602487</rx><tx>50675141</tx></day>
                <day id="7"><date><year>2015</year><month>01</month><day>04</day></date><rx>24527664</rx><tx>12304414</tx></day>
               </days>
               <months>
                <month id="0"><date><year>2015</year><month>01</month></date><rx>88311907</rx><tx>173398135</tx></month>
               </months>
               <tops>
                <top id="0"><date><year>2015</year><month>01</month><day>05</day></date><time><hour>00</hour><minute>00</minute></time><rx>28602487</rx><tx>50675141</tx></top>
                <top id="1"><date><year>2015</year><month>01</month><day>09</day></date><time><hour>00</hour><minute>00</minute></time><rx>6580611</rx><tx>30690740</tx></top>
                <top id="2"><date><year>2015</year><month>01</month><day>04</day></date><time><hour>21</hour><minute>00</minute></time><rx>24527664</rx><tx>12304414</tx></top>
                <top id="3"><date><year>2015</year><month>01</month><day>08</day></date><time><hour>00</hour><minute>00</minute></time><rx>11726428</rx><tx>21680669</tx></top>
                <top id="4"><date><year>2015</year><month>01</month><day>07</day></date><time><hour>00</hour><minute>00</minute></time><rx>4884754</rx><tx>24626526</tx></top>
                <top id="5"><date><year>2015</year><month>01</month><day>06</day></date><time><hour>00</hour><minute>00</minute></time><rx>3288758</rx><tx>19551164</tx></top>
                <top id="6"><date><year>2015</year><month>01</month><day>10</day></date><time><hour>00</hour><minute>00</minute></time><rx>8514439</rx><tx>13464434</tx></top>
               </tops>
               <hours>
                <hour id="0"><date><year>2015</year><month>01</month><day>11</day></date><rx>16934</rx><tx>5891</tx></hour>
                <hour id="1"><date><year>2015</year><month>01</month><day>11</day></date><rx>7742</rx><tx>5711</tx></hour>
                <hour id="2"><date><year>2015</year><month>01</month><day>11</day></date><rx>9844</rx><tx>6126</tx></hour>
                <hour id="3"><date><year>2015</year><month>01</month><day>11</day></date><rx>14243</rx><tx>6017</tx></hour>
                <hour id="4"><date><year>2015</year><month>01</month><day>11</day></date><rx>11698</rx><tx>5804</tx></hour>
                <hour id="5"><date><year>2015</year><month>01</month><day>11</day></date><rx>7126</rx><tx>5507</tx></hour>
                <hour id="6"><date><year>2015</year><month>01</month><day>11</day></date><rx>7931</rx><tx>5601</tx></hour>
                <hour id="7"><date><year>2015</year><month>01</month><day>11</day></date><rx>7025</rx><tx>5497</tx></hour>
                <hour id="8"><date><year>2015</year><month>01</month><day>11</day></date><rx>7625</rx><tx>5591</tx></hour>
                <hour id="9"><date><year>2015</year><month>01</month><day>11</day></date><rx>52042</rx><tx>329932</tx></hour>
                <hour id="10"><date><year>2015</year><month>01</month><day>11</day></date><rx>42753</rx><tx>21062</tx></hour>
                <hour id="11"><date><year>2015</year><month>01</month><day>11</day></date><rx>1803</rx><tx>2308</tx></hour>
                <hour id="12"><date><year>2015</year><month>01</month><day>10</day></date><rx>505311</rx><tx>296799</tx></hour>
                <hour id="13"><date><year>2015</year><month>01</month><day>10</day></date><rx>120184</rx><tx>107789</tx></hour>
                <hour id="14"><date><year>2015</year><month>01</month><day>10</day></date><rx>72727</rx><tx>74352</tx></hour>
                <hour id="15"><date><year>2015</year><month>01</month><day>10</day></date><rx>44956</rx><tx>21084</tx></hour>
                <hour id="16"><date><year>2015</year><month>01</month><day>10</day></date><rx>7864</rx><tx>5376</tx></hour>
                <hour id="17"><date><year>2015</year><month>01</month><day>10</day></date><rx>37045</rx><tx>1178931</tx></hour>
                <hour id="18"><date><year>2015</year><month>01</month><day>10</day></date><rx>38688</rx><tx>496493</tx></hour>
                <hour id="19"><date><year>2015</year><month>01</month><day>10</day></date><rx>8299</rx><tx>6004</tx></hour>
                <hour id="20"><date><year>2015</year><month>01</month><day>10</day></date><rx>17799</rx><tx>12670</tx></hour>
                <hour id="21"><date><year>2015</year><month>01</month><day>10</day></date><rx>14367</rx><tx>15995</tx></hour>
                <hour id="22"><date><year>2015</year><month>01</month><day>10</day></date><rx>8752</rx><tx>7657</tx></hour>
                <hour id="23"><date><year>2015</year><month>01</month><day>10</day></date><rx>7733</rx><tx>6004</tx></hour>
               </hours>
              </traffic>
             </interface>
            </vnstat>'''
        return xmltodict.parse(z)
