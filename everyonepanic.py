import contextlib
import json
import os
import urllib2
import webapp2
from twilio.rest import TwilioRestClient

# Calls you when your sites go down.
# License is GPLv3.
# Author: Eric Jiang <eric@doublemap.com>

TWILIO_SID = os.environ['TWILIO_SID']
TWILIO_TOKEN = os.environ['TWILIO_TOKEN']
TWILIO_FROM = os.environ['TWILIO_FROM']
CALLEES = os.environ['CALLEES'].split(',')

UPTIME_ROBOT_KEY = os.environ['UPTIME_ROBOT_KEY']
UPTIME_ROBOT = "http://api.uptimerobot.com/getMonitors?apiKey=" + UPTIME_ROBOT_KEY + "&format=json&noJsonCallback=1"

# what's our app name?
APP_HOSTNAME = "YOUR_APP_HERE.appspot.com"
if 'APP_HOSTNAME' in os.environ:  # try environment
    APP_HOSTNAME = os.environ['APP_HOSTNAME']
else:  # try getting it from app engine
    try:
        from google.appengine.api.app_identity import get_application_id
        APP_HOSTNAME = get_application_id() + ".appspot.com"
    except ImportError:
        pass


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hi, this thing will call you if uptime robot reports down sites.')


def get_uptime_status():
    with contextlib.closing(urllib2.urlopen(UPTIME_ROBOT)) as ustream:
        resp = json.load(ustream)

    downsites = []

    for m in resp['monitors']['monitor']:
        if m['status'] == "9":  # 9 == "Down", 8 == "Seems down"
            downsites.append(m['friendlyname'])
    return {"total": len(resp['monitors']['monitor']), "down": len(downsites), "downsites": downsites}


def trigger_call(recipients):
    client = TwilioRestClient(TWILIO_SID, TWILIO_TOKEN)
    for recp in recipients:
        call = client.calls.create(url=("http://%s/downmessage" % APP_HOSTNAME),
            to=recp, from_=TWILIO_FROM)


class CheckUptimes(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        res = get_uptime_status()
        self.response.write("%d sites being monitored\n" % res['total'])
        if res['down'] != 0:
            self.response.write("Everybody panic!\n")
            for site in res['downsites']:
                self.response.write("%s is down.\n" % site)
            trigger_call(CALLEES)
        else:
            self.response.write("Everything seems fine\n")


class DowntimeMessage(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = "text/xml"
        res = get_uptime_status()
        if res['down'] != 0:
            self.response.write("""<?xml version="1.0" encoding="UTF-8"?>
            <Response>
                <Say voice="alice">Everyone panic! %s</Say>
            </Response>""" % " ".join(map(lambda s: ("%s is down." % s.replace("doublemap", "double map")), res['downsites'])))
        else:
            self.response.write("""<?xml version="1.0" encoding="UTF-8"?>
            <Response>
                <Say voice="alice">False alarm. %d of %d sites are down.</Say>
            </Response>""" % (res['down'], res['total']))


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/checksites', CheckUptimes),
    ('/downmessage', DowntimeMessage),
], debug=True)
