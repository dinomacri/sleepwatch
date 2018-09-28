from datetime import datetime, time
import urllib3
import configparser
import sys
import paramiko
from wakeonlan import send_magic_packet

# Creates an object for the datetime module
now = datetime.now()
now_time = now.time()

# Creates an object for the Config Parser
config = configparser.ConfigParser()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Reads the config file
try:
    # Creates an object for the Config Parser
    config = configparser.ConfigParser()
    config.read("config")
except FileNotFoundError as error:
    sys.exit(error)

# General configuration options
if config.has_option('General', 'Enabled'):
    enabled = config.getboolean('General', 'Enabled')
else:
    enabled = False

if config.has_option('General', 'StartTime'):
    starttime = time(int(config.get('General', 'StartTime')))

if config.has_option('General', 'EndTime'):
    endtime = time(int(config.get('General', 'EndTime')))

# Wake on Lan configuration options
if config.has_option('WOL', 'Enabled'):
    WOLEnabled = config.getboolean('WOL', 'Enabled')
else:
    WOLEnabled = True

if config.has_option('WOL', 'MACAddress'):
    WOLMACAddress = config.get('WOL', 'MACAddress')

# SSH Shutdown module
if config.has_option('SSH', 'Address'):
    SSHAddress = config.get('SSH', 'Address')

if config.has_option('SSH', 'Port'):
    SSHPort = int(config.get('SSH', 'Port'))

if config.has_option('SSH', 'User'):
    SSHUser = config.get('SSH', 'User')

if config.has_option('SSH', 'Password'):
    SSHPass = config.get('SSH', 'Password')

if config.has_option('SSH', 'Command'):
    SSHCommand = config.get('SSH', 'Command')
else:
    SSHCommand = "systemctl poweroff"

# Plex module configuration options
if config.has_option('Plex', 'Enabled'):
    plexenabled = config.getboolean('Plex', 'Enabled')
else:
    plexenabled = False

if config.has_option('Plex', 'Hostname'):
    hostname = config.get('Plex', 'Hostname')
else:
    sys.exit("ERROR: Missing option from [PLEX] in config: hostname")

if config.has_option('Plex', 'Port'):
    plexport = config.get('Plex', 'Port')
else:
    plexport = 32400

if config.has_option('Plex', 'HTTP'):
    http = config.getboolean('Plex', 'HTTP')
else:
    http = False

if config.has_option('Plex', 'QueryPath'):
    querypath = config.get('Plex', 'QueryPath')
else:
    querypath = "/status/sessions"

if http == False:
    httpsprefix = "https://"
else:
    httpsprefix = "http://"

absoluteurl = httpsprefix + hostname + ":" + plexport + querypath

# Creates an object for urllib3 to make requests
http = urllib3.PoolManager()

def sshshutdown():
    try:
        print("Establishing connection with SSH Server")
        ssh.connect(SSHAddress, port=SSHPort, username=SSHUser, password=SSHPass)
        print("Sending command execution to systemctl for shutdown")
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(SSHCommand)
        print (ssh_stdout)
    except paramiko.SSHException as error:
        sys.exit("ERROR: " + str(error))
    finally:
        ssh.close()

def wolwake():
    if WOLEnabled == True:
        print("WOL is enabled. Waking Server.")
        send_magic_packet(WOLMACAddress)
    if WOLEnabled == False:
        sys.exit("WOL is disabled. Server is offline.")


def checktime():
    if starttime <= now_time <= endtime:
        print ("The current time is within the offline hours range. Checking for plex status")
        if checkplex() == 1:
            sshshutdown()
        return 1
    else:
        print("Current time is not within offline hours range, checking if host is online and if WOL is enabled.")
        wolwake()

# Function checks response to see if any content is being watched
def checkplex():
    if plexenabled:
        # Makes a GET request to the plex server
        try:
            print('Connecting to Plex: ' + hostname + '...')
            request = http.request('GET', absoluteurl, timeout=3)
            print('Connection Success')
            # Stores request data in variable
            response = str(request.data)

            if 'MediaContainer size="0"' in response:
                print("No plex content is being viewed. Proceeding.")
                return 1
            elif "MediaContainer size=" in response:
                sys.exit("Plex content is being viewed. Aborting.")
            else:
                sys.exit("ERROR: Invalid XML")
        except:
            sys.exit("ERROR: Plex is offline and within offline hours. All good man ")

checktime()
