#!/usr/bin/python

from phue import Bridge
import requests
import sys
import logging
from pprint import pprint
import smtplib
import ConfigParser

logging.basicConfig(level=logging.INFO)
# print a log message to the console.
logging.debug('LightMonitor Started')

Config = ConfigParser.ConfigParser()
Config.read("LightMonitor.ini")

try:
   Email_To=Config.get('Email', 'TO')
   Email_Server=Config.get('Email', 'Server')
   Email_Port=Config.getint('Email', 'Port')
   Email_User=Config.get('Email', 'User')
   Email_Password=Config.get('Email', 'Password')

   Room_Prefix=Config.get('Room', 'Prefix')
except:
   sys.exit("The LightMonitor.ini file is missing a required field")

def send_mail(Server,Port,User,Password, To, Subject,Msg):
   server = smtplib.SMTP_SSL(Server, Port)
   server.login(User,Password)
   mail="Subject: " + Subject + "\n\n" + Msg
   logging.info("Sending email to: {} Subject: {}".format(To,Subject))
   server.sendmail("huemonitor@alerts.trimbletools.com",To,mail)
   server.quit()

try:
   r = requests.get('https://discovery.meethue.com')
except:
   logging.error("Could not connect to discovery service")
   sys.exit ("Could not connect to discovery service")

r.status_code == requests.codes.ok
#print requests.codes.ok
bridges=r.json()

if len(bridges) != 1 :
   logging.error("There is not one bridge at the location. There are {} bridges".format(len(bridges)))
   sys.exit ("There is not one bridge at the location. There are {} bridges".format(len(bridges)))

bridge_ip=bridges[0]["internalipaddress"]
logging.info("Bridge IP: {}".format(bridge_ip))
b = Bridge(bridge_ip)

# If the app is not registered and the button is not pressed, press the button and call connect() (this only needs to be run a single time)
b.connect()

# Get the bridge state (This returns the full dictionary that you can explore)
#b.get_api()
lights = b.get_light_objects('name')
#pprint (lights)
#print len(lights)
Room_On=False
Room_Lights="The Following {} Lights are on\n".format(Room_Prefix)
for light in lights:
   logging.debug("Light: {} Reachable: {}".format(light, lights[light].reachable))
   if light.startswith(Room_Prefix):
      logging.info("Light: {} Reachable: {}".format(light, lights[light].reachable))
      if lights[light].reachable:
         logging.info("Light On in {}: Light: {} Reachable: {}".format(Room_Prefix,light, lights[light].reachable))
         Room_On=True
         Room_Lights+=light+"\n"
if Room_On:
   send_mail(Email_Server,Email_Port,Email_User,Email_Password, Email_To,"{} lights on".format(Room_Prefix),Room_Lights)
logging.debug('LightMonitor Ended')
