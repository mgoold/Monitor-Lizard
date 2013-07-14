#!/usr/local/bin/python2.7


#IMPORTS
import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')
sys.path.append('/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/cx_Oracle-5.1.2-py2.7-macosx-10.6-intel.egg')
sys.path.append('/usr/local/bin')
sys.path.append('/usr/local/lib/python2.7/site-packages/cx_Oracle-5.1.2-py2.7-macosx-10.8-intel.egg')
sys.path.append('/usr/local/bin/python2.7')
sys.path.append('/usr/bin')
sys.path.append('/sbin')
sys.path.append('/bin')
sys.path.append('/etc')

import sqlalchemy
from sqlalchemy import *
import cx_Oracle
import numpy as np
import os, traceback, csv, codecs, decimal, datetime, string,time
from datetime import *
from html import HTML
import sqlalchhelp as sqh

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import operator

temp = sys.stdout #store original stdout object for later
sys.stdout = open('C:\Users\mgoold\Documents\Python_Alerts_Project\log.html','w')

fname='C:\Users\mgoold\Documents\Python_Alerts_Project\successlog.txt'

class autoviv(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

# of minutes between attempts to try and send message
if sqh.eval_test_time(fname,420)==1:
	#"oracle+cx_oracle://DWUSERNAME:dwpw@fulldns"
	db = create_engine("oracle+cx_oracle://DWUSERNAME:dwpw@fulldns")

	# db.echo = False  # Try changing this to True and see what happens

	db_con = db.connect()

	sqlstr = open('/Users/mgoold/Documents/Python_Alerts_Project/CTT_Breakout_BY_DAY_6.30.13FF.txt', 'r').read()

	alert_data=db_con.execute(sqlstr)

	# print 'alert_data', alert_data

	checklist={'clicks_by_day_ty':{'index':'day_id','l':-.2,'ld':3,'d':{'MEDIA_SEARCH_TYPE_DESC':{'l':0,'m':'CLICKS_TY'},'COMPETITOR_NAME':{'l':0,'m':'CLICKS_TY'},'BROWSER_DESC':{'l':0,'m':'CLICKS_TY'}}}}

	alert_output=sqh.get_alert_dict(alert_data, checklist)

	# print 'alert_output', alert_output

	checkup=sqh.alert_eval(alert_output,checklist)

	print str(checkup)

	h=sqh.alert_html(checklist,checkup)
	
	db_con.close()

	# me == my email address
	# you == recipient's email address
	me = "username@hotwire.com"  # you may wish to 
	you = "recipientname@hotwire.com"

	# Create message container - the correct MIME type is multipart/alternative.
	msg = MIMEMultipart('alternative')
	msg['Subject'] = "Link"
	msg['From'] = me
	msg['To'] = you

	# Record the MIME types of both parts - text/plain and text/html.
	part1 = MIMEText(h, 'html')

	# Attach parts into message container.
	# According to RFC 2046, the last part of a multipart message, in this case
	# the HTML message, is best and preferred.
	msg.attach(part1)

	# Send the message via local SMTP server.
	s = smtplib.SMTP('shost.sea.corp.expecn.com',25)

	# sendmail function takes 3 arguments: sender's address, recipient's address
	# and message to send - here it is sent as one string.
	s.sendmail(me, you, msg.as_string())
	s.quit()

	sqh.set_test_time(fname)

	sys.stdout = temp #restore print commands to interactive prompt
	sys.stdout.close() #ordinary file object
