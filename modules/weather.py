#!/usr/bin/env python
# -*- coding: utf-8 -*-

import htpc
import cherrypy
import requests
import geocoder
import logging
from cherrypy.lib.auth2 import require


class Weather(object):
    def __init__(self):
        self.logger = logging.getLogger('modules.weather')
        htpc.MODULES.append({
            'name': 'Weather',
            'id': 'weather',
            'fields': [
                {'type': 'bool', 'label': 'Enable', 'name': 'weather_enable'},
                {'type': 'text', 'label': 'Menu name', 'name': 'weather_name'},
                {'type': 'text', 'label': 'ForcastIO apikey', 'placeholder': '', 'desc': '', 'name': 'weather_apikey'},
                {'type': 'text', 'label': 'Latitude', 'placeholder': 'optional', 'desc': 'ForcastIO will your lat, long based your ip if left blank', 'name': 'weather_latitude'},
                {'type': 'text', 'label': 'Longitude', 'placeholder': 'optional', 'desc': '', 'name': 'weather_longitude'}
            ]
        })

    def get_location(self):
        # q maxmind for ip, then use freegeoip lat long as is more accurate
        md = geocoder.maxmind('me')
        location = geocoder.freegeoip(md.ip)
        d = {"lat": location.lat,
             "long": location.lng
        }
        return d

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def fetch(self):
        apikey = htpc.settings.get('weather_apikey')
        lat = htpc.settings.get('weather_latitude')
        Long = htpc.settings.get('weather_longitude')
        # Find long and lat based in ip
        if not lat and not Long:
            cords = self.get_location()
            lat = cords["lat"]
            Long = cords["long"]
        url = 'https://api.forecast.io/forecast/%s/%s,%s?units=ca' % (apikey, lat, Long)
        r = requests.get(url)
        return r.json()
