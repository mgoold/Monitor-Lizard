#!/usr/local/bin/python2.7

import sys
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


def eval_test_time(fname,int):
  try:
		if os.stat(fname)[6]==0:
			print 'no lines in file'
			pass
		else:
			print 'trying to open file.'
			s=open(fname,'r')
			lines=s.readlines()
			print 'line', lines[1]
			print 'dt', lines[1].split()[1]
			testdate=lines[1].split('.')[0]
			print 'testdate', testdate
			print 'now', datetime.now()
			testdate=datetime.strptime(lines[1].split('.')[0],"%Y-%m-%d %H:%M:%S")
			now=str(datetime.now())
			now=datetime.strptime(now.split('.')[0],"%Y-%m-%d %H:%M:%S")
			interval=int
			t=now-testdate
			print 't', t
	
			t=((t.days*86500)+t.seconds)
			t=t/60 #time in minutes
			print 't', t
			test=0
			if t>=interval:
				test=1
				print 'more than '+str(interval)+ 'hrs passed; rerunning'
			elif t<interval:
				print 'less than '+str(interval)+' hrs passed'
				print 'exiting...'
			
		return test
		
		
	except IOError: 
		print 'IOError occurred...'
		pass
		sys.exit()

def set_test_time(fname):
	try:
		f=open(fname,'w')
		f.write('Success'+ "\n")
		f.write(str(datetime.now())+ "\n")
		f.close()
	except URLError:
		print URLError.code

def alert_html(checklist,checkup):	
	h = HTML()	
	try:
		for key in checklist.keys():
			# If the key exceeds a threshhold, look for drivers.
		# 	print '''checkup[key]['Abs_Avg_Day_Diff']''',checkup[key]['Abs_Avg_Day_Diff']
		# 	print '''checklist[key]['l'])''', checklist[key]['l']
			if float(checkup[key]['Abs_Avg_Day_Diff'])>float(checklist[key]['l']): 
		# 		
		# 		#generate alert text
				txt=key+'value of '+str(checkup[key]['Abs_Avg_Day_Diff'])+' is over alert threshold of '+str(checklist[key]['l'])
				print txt
				h.p(txt)
		# 		
		# 		#run driver analytics
				lev=0
		# 		# for this dependent variable, get the list of driver variables.
				driverlist=checklist[key]['d']
		# 		
		# 		print 'driverlist', driverlist		
		# 		print '''driverlist[key]['l']''', checklist[key]['l']
			
				for driver in driverlist.keys():
					lev=driverlist[driver]['l']
		# 			# if no driver-level threshold was provided...
					if lev==0:
						lev=checklist[key]['l']
					subdrivlist=checkup[driver]
					for subdriv in subdrivlist.keys():
		# 				print 'subdrivlist', subdrivlist[subdriv]
		# 	# 				# default to the same threshold for the primary variable
		# 				print '''checkup[key]['Day_Avg_Diff']''', checkup[key]['Day_Avg_Diff']
		# 				print '''sign(subdrivlist[subdriv]['Day_Avg_Diff'])''', subdrivlist[subdriv]['Day_Avg_Diff']
				
				
						if sign(checkup[key]['Day_Avg_Diff'])==sign(subdrivlist[subdriv]['Day_Avg_Diff']):
							# and it's over the threshold...
							driverlev=subdrivlist[subdriv]['Day_Avg_Diff']
		# 					print 'triverlev', driverlev, 'lev', lev
		# 					print '''abs(driverlev)''',abs(driverlev), '''abs(lev)''',abs(lev)
							if abs(driverlev)>abs(lev):
								# generate driver text note
								txt=' Driver variable '+driver+':'+subdriv+' is at '+ str(subdrivlist[subdriv]['Day_Avg_Diff'])
								print txt
						h.p(txt)
		return h
	except:
		e = sys.exc_info()[0]
		el=sys.exc_traceback.tb_lineno
		print 'Error: %s' % e 
		print 'lineno: %s' % el	

def sign(input):
	sign=0
	try:
		if input<0:
			sign=-1
		elif input>0:
			sign=1
	
		return sign
	
	except: # catch *all* exceptions
		e = sys.exc_info()[0]
		print 'Error: %s' % e 
		
def alert_eval(alert_output,checklist):
	try:
		eo=autoviv()

		for key in checklist.keys():	
			ld=int(checklist[key]['ld'])
# 			print 'ld', ld
# 			print 'key', key, alert_output[key]
			intlist=alert_output[key].keys()
# 			print 'intlist', intlist
			intlist.sort(key=int)
# 			print 'intlist after sort', intlist
			tempvals=[]
	
			for intkey in intlist:

				tempvals.append(alert_output[key][intkey])          	
		
			eo[key]['s_per']=np.mean(tempvals[:-ld]) #use numpy to average all days prior to last 3
			temp_pcts=[]
			for i in range(1,ld+1):
				dayval=tempvals[-(i)]
				temp_pcts.append((dayval-eo[key]['s_per'])/eo[key]['s_per'])
	
			eo[key]['temp_pcts']=temp_pcts
			eo[key]['Day_Avg_Diff']=np.mean(temp_pcts) #use numpy to average last 3 days.
			eo[key]['Abs_Avg_Day_Diff']=abs(eo[key]['Day_Avg_Diff'])
			
			for driver in checklist[key]['d']:
				for subdriv in alert_output[driver].keys():		
# 					print 'subdriv', subdriv	
# 					print 'subdridict', alert_output[driver][subdriv]	
					intlist=alert_output[driver][subdriv].keys()
# 					print 'intlist', intlist

					if len(intlist)>2*ld:
						intlist.sort(key=int)
						tempvals=[]

						for intkey in intlist:
							tempvals.append(alert_output[driver][subdriv][intkey])          	
						eo[driver][subdriv]['s_per']=np.mean(tempvals[:-ld]) #use numpy to average all days prior to last 3
						temp_pcts=[]
						for i in range(1,ld+1):
							dayval=tempvals[-(i)]
							temp_pcts.append((dayval-eo[driver][subdriv]['s_per'])/eo[driver][subdriv]['s_per'])
	
						eo[driver][subdriv]['temp_pcts']=temp_pcts
						eo[driver][subdriv]['Day_Avg_Diff']=np.mean(temp_pcts) #use numpy to average last 3 days.
						eo[driver][subdriv]['Abs_Avg_Day_Diff']=abs(eo[driver][subdriv]['Day_Avg_Diff'])				
			
		return eo

	except: # catch *all* exceptions
		e = sys.exc_info()[0]
		el=sys.exc_traceback.tb_lineno
		print 'Error: %s' % e 
		print 'lineno: %s' % el
		
def get_alert_dict(alert_data, arg_list):
	try:
		ad=autoviv()	
		for row in alert_data:		
			for key in arg_list.keys():
				date_column=arg_list[key]['index']
				if ad[key][row[date_column]] not in ad[key].keys():
					ad[key][row[date_column]]=row[key]
				for driver in arg_list[key]['d']:
					met_col=arg_list[key]['d'][driver]['m'].lower()
					if row[date_column] not in ad[driver][row[driver.lower()]].keys():
						ad[driver][row[driver.lower()]][row[date_column]]=row[met_col]
					else:
						temp_val=ad[driver][row[driver.lower()]][row[date_column]]
						ad[driver][row[driver.lower()]][row[date_column]]=temp_val+row[met_col]
						
		return ad
	except: # catch *all* exceptions
		e = sys.exc_info()[0]
		print 'Error: %s' % e 
