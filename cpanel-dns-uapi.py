#!/usr/bin/env python3
APP_NAME='cPanel-DNS-UAPI'
APP_VERSION='v21122'

import base64, json, sys
from os import environ
from pathlib import Path
from requests import Session
from tldextract import extract
from dotenv import load_dotenv
from urllib.parse import quote
from os.path import realpath, dirname, join

ENVCONTENT = '''
# cpanel-dns-api configuration file

CPANEL_DOMAIN = example.com
CPANEL_PORT = 2083
CPANEL_USERNAME = username
CPANEL_PASSWORD = password

DNS_ZONE = example.com
RECORD_TTL = 3600
'''

# Verify execution type
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'): # Exe bundle
	envlocation = join(dirname(sys.executable), '.dns-env')
else: # Python script
	envlocation = join(dirname(__file__), '.dns-env')

# Verify env file existence
if not Path(envlocation).is_file():
	print('.dns-env MISSING, CREATING AN EMPTY ONE, CUSTOMIZE IT')
	print('--> NEW ENV LOCATION: {}'.format(envlocation))
	with open(envlocation, 'w+') as text_file:
		text_file.writelines(ENVCONTENT)
	sys.exit(0)

# Load env file
load_dotenv(envlocation)
DASHBOARD = environ.get("CPANEL_DOMAIN")
ZONE = environ.get("DNS_ZONE")
PORT = environ.get('CPANEL_PORT')
USERNAME = environ.get('CPANEL_USERNAME')
PASSWORD = environ.get('CPANEL_PASSWORD')
RECORD_TTL = environ.get('RECORD_TTL')

class PanelToken:
	def __init__(self):
		self.security_token = None

	def update_token(self, token):
		self.security_token = token

class ZoneSerial:
	def __init__(self):
		self.serial = None

	def update_serial(self, serial):
		self.serial = int(serial)

class RequestHeader:
	def __init__(self):
		self.header = {}

	def generate_header(self):
		self.header = {
		"accept-encoding": "gzip, deflate, br",
		"accept": "*/*",
		"connection": "keep-alive"
		}

token = PanelToken()
serial = ZoneSerial()
header = RequestHeader()
s = Session()

def login(): # Perform login on cPanel dashboard
	def launch_request():
		header.generate_header()
		url = "https://{}:{}/login/?login_only=1".format(DASHBOARD, PORT)

		data = {
		"user" : USERNAME,
		"pass" : PASSWORD
		}

		req = s.post(url, headers=header.header, data=data)

		if req.json()['status'] == 0:
			print('LOGIN ERROR')
			print()
			print(req.json())
		else:
			token.update_token(req.json()['security_token'][1:])

	return launch_request()

def get_serial(): # Get serial of the ZONE
	def launch_request():
		header.generate_header()
		url = "https://{}:{}/{}/execute/DNS/parse_zone?zone={}".format(DASHBOARD, PORT, token.security_token, ZONE)

		req = s.get(url, headers=header.header)

		if not req.json()['errors']:
			serial.update_serial(base64.b64decode(req.json()['data'][3]['data_b64'][2]).decode("utf8"))
		else:
			print('GET SERIAL ERROR')
			print()
			print(req.json())

	return launch_request()

def add_record(RECORD, TOKEN): # Add a TXT record
	get_serial()
	def launch_request():
		header.generate_header()
		url = "https://{}:{}/{}/execute/DNS/mass_edit_zone?zone={}".format(DASHBOARD, PORT, token.security_token, ZONE)

		data = '{{"dname":"{}.","ttl":{},"record_type":"TXT","data":["{}"]}}'.format(RECORD, RECORD_TTL, TOKEN)
		record = 'zone={}&serial={}&add={}'.format(ZONE, serial.serial, quote(data))
		global req
		req = s.post(url, headers=header.header, data=record)
		if not req.json()['errors']:
			print('ADD WAS SUCCESSFUL')
		else:
			print('ADD FAILED')
			print()
			print(req.json())

	return launch_request()

def _del_record(ID): # Direct function to delete a record (Get called only by parse_and_delete)
	get_serial()
	def launch_request():
		header.generate_header()
		url = "https://{}:{}/{}/execute/DNS/mass_edit_zone?zone={}".format(DASHBOARD, PORT, token.security_token, ZONE)

		data = {
		"serial": serial.serial,
		"remove": ID
		}

		req = s.post(url, headers=header.header, data=data)
		if not req.json()['errors']:
			print('DELETE WAS SUCCESSFUL')
		else:
			print('DELETE FAILED')
			print()
			print(req.json())

	return launch_request()

def parse_and_delete(RECORD, TOKEN): # Parse and delete given TXT record
	def launch_request():
		header.generate_header()
		url = "https://{}:{}/{}/execute/DNS/parse_zone?zone={}".format(DASHBOARD, PORT, token.security_token, ZONE)

		req = s.get(url, headers=header.header)

		return req.json()

	response = launch_request()

	for item in response['data']:
		if 'record_type' in item:
			if item['record_type'] == 'TXT':
				record_found = base64.b64decode(item['dname_b64']).decode('utf-8')
				token_found = base64.b64decode(item['data_b64'][0]).decode('utf-8')
				if (extract(RECORD).subdomain in record_found) and (TOKEN in token_found):
					return _del_record(item['line_index'])

	print('DELETE FAILED - NO RECORD FOUND')

#### BEGIN
if ZONE != 'example.com':
	login()
else:
	print('WORKING WITH DEFAULT ENV FILE, PLEASE CUSTOMIZE')
	print('--> ENV LOCATION: {}'.format(envlocation))
	sys.exit(1)

if not sys.flags.interactive:
	if len(sys.argv) == 1:
		print('APP_NAME: {}'.format(APP_NAME))
		print('APP_VERSION: {}'.format(APP_VERSION))
		print()
		print("Loaded cPanel Dashboard: {}".format(DASHBOARD))
		print("Loaded Port: {}".format(PORT))
		print("Loaded Username: {}".format(USERNAME))
		print("Loaded Password: {} (Masked)".format(PASSWORD.translate("*"*256)))
		print()
		print("Loaded DNS Zone: {}".format(ZONE))
		print("Loaded TTL: {}".format(RECORD_TTL))
		print('------------------')
		print('MISSING ARGUMENTS:')
		print()
		print('ADD FQDN TOKEN')
		print('DELETE FQDN TOKEN')
		print()
		print('EXAMPLE: ADD _acme-challenge.example.com DGyRejmCefe7v4NfDGDKfA')
	elif sys.argv[1] == 'ADD': # Add record
		add_record(sys.argv[2], sys.argv[3])
	elif sys.argv[1] == 'DELETE': # Delete record
		parse_and_delete(sys.argv[2], sys.argv[3])
