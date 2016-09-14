import pyodbc
import itertools
import urllib
import requests
from requests_toolbelt import SSLAdapter
import ssl
import plivo
import pandas as pd
import win32com.client
from geopy.distance import vincenty
from geopy.geocoders import GoogleV3
from geopy.exc import GeocoderTimedOut, GeocoderAuthenticationFailure
from random import randint
from time import sleep
from werkzeug import generate_password_hash, check_password_hash
import config


def email(mail_to, mail_subj, mail_body, mail_cc=None, mail_attach=None, mail_html=False):
    import pythoncom
    pythoncom.CoInitialize()
    olMailItem = 0x0
    obj = win32com.client.Dispatch("Outlook.Application")
    msg = obj.CreateItem(olMailItem)
    msg.To = mail_to
    if mail_cc:
        msg.CC = mail_cc
    msg.Subject = mail_subj
    if mail_attach:
        for attach in mail_attach:
            msg.Attachments.Add(attach)
    if mail_html:
        msg.HTMLBody = mail_body
    else:
        msg.Body = mail_body
    msg.Send()


def dbQuery(string, conn, params=None):
    if conn.upper() == 'EDW':
        cnnx = pyodbc.connect('DRIVER={IBM DB2 ODBC DRIVER - DB2COPY1};DBALIAS=EDW5P1;UID=' + config.usr + ';PWD=' + config.fbpass)
    elif conn.upper() == 'JIVA':
        cnnx = pyodbc.connect('DRIVER={Oracle in OraClient11g_home1};DBQ=JHCMPREP;UID=' + config.usr + ';PWD=' + config.fbpass)
    else:
        raise ValueError('Unrecognized DB connection identifier')
    result = pd.read_sql_query(string, cnnx, params=params)
    cnnx.close()
    return result


def geocode(address):
    googleGeo = GoogleV3(config.googleKey) # Google Maps v3 API geolocator
    location = None
    attempt = 0
    useGoogle = True #False
    useMapQuest = False
    while (location == None) and (attempt <= 8):
        try:
            attempt += 1
            if useGoogle:
                location = googleGeo.geocode(address, timeout=10)
            else:
                location = nomiGeo.geocode(address, timeout=10)
                if location == None:
                    useGoogle = True
                    location = googleGeo.geocode(address, timeout=10)
            sleep(randint(1,3)) # Give the API a break
        except GeocoderAuthenticationFailure:
            print 'Error: GeocoderAuthenticationFailure while geocoding %s during attempt #%s' % (address, str(attempt))
            if attempt % 2 == 0:
                useGoogle = True
            else:
                useGoogle = False
                sleep(60)
        except GeocoderTimedOut:
            sleep(randint(1,3)) # Give API a break
            print 'Error: GeocoderTimedOut while geocoding %s during attempt #%s' % (address, str(attempt))
    return location


class pyChart(object):
    def __init__(self, chartType, renderTo, title, subtitle=None, xLab=None, yLab=None, series=None, credits=None):
        self.chartType = chartType

        if series:
            self.series = series
        else:
            self.series = []

        self.chart = {
            'chart': {
                'type': chartType,
                'renderTo': renderTo
            },
            'title': {
                'text': title
            },
            'series': self.series
        }

        if chartType in ['column','bar','line','spline']:
            self.chart['yAxis'] = {'title': {'text': yLab}}
            self.chart['xAxis'] = {'categories': xLab}
        elif chartType in ['pie']:
            self.chart['series'] = [{'name': xLab, 'colorByPoint': 1, 'data': []}]
        elif chartType in ['scatter','bubble']:
            self.chart['yAxis'] = {'title': {'text': yLab}}
            self.chart['xAxis'] = {'title': {'text': xLab}}
        else:
            pass

        if credits:
            self.chart['credits'] = {'text': credits[0], 'href': credits[1]}
        else:
            self.chart['credits'] = {'enabled': 0}

        if subtitle:
            self.chart['subtitle'] = {'text': subtitle}

    def addToSeries(self, name, data):
        if self.chartType in ['column','bar','line','spline']:
            self.chart['series'].append({'name': name, 'data': data})
        elif self.chartType in ['pie']:
            self.chart['series'][0]['data'].append({'name': name, 'data': data})
        elif self.chartType in ['scatter','bubble']:
            self.chartType['series'][0]['data'].append({'name': name, 'data': data})
        else:
            pass

    def formatPoint(self, format):
        self.chart['tooltip'] = {'pointFormat': format}

    def generate(self):
        return self.chart


class Outreach(object):
    def text(self, number, message):
        params = {
            'src': config.plivoNum,
            'dst': number,
            'text': message
        }
        
        try:
            p = plivo.RestAPI(config.plivoID, config.plivoToken)
            response = p.send_message(params)
            return response
        except:
            return '{"status": 401, "message": "SSL_VERIFY_ERROR"}'

    def call(self, number, message):
        params = {
            'api_key': config.nexmoKey,
            'api_secret': config.nexmoSecret,
            'from': config.nexmoNum,
            'to': number,
            'text': message
        }

        try:
            url = 'https://api.nexmo.com/tts/json?' + urllib.urlencode(params)
            headers = {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            s = requests.Session()
            s.mount(url, SSLAdapter(ssl.PROTOCOL_TLSv1_2))
            response = s.get(url, headers=headers, verify=config.certsPath + 'certs.pem').text
            #response = requests.get(url, headers=headers, verify=config.certsPath + 'certs.pem').text
            #request = urllib2.Request(url, None, {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'})
            #response = urllib2.urlopen(request)
            return response
        except:
            #return 'SSL_VERIFY_ERROR: Corporate network blocked the outgoing SSL request'
            return '{"status": 401, "message": "SSL_VERIFY_ERROR"}'