import time
import utime
import gsm
import machine
from machine import Pin

def gsm_module_power():
	GSM_PWR = Pin(4, Pin.OUT)
	GSM_RST = Pin(5, Pin.OUT)
	GSM_MODEM_PWR = Pin(23, Pin.OUT)

	GSM_PWR.value(0)
	GSM_RST.value(1)
	GSM_MODEM_PWR.value(1)


def gsm_start(led_pin):
	led_pin.value(0)
	gsm.stop() # in case we are retrying a connection, just to be safe

	time.sleep(1)

	gsm.start(tx=27, rx=26, apn='', user='', password='')

	connection = False
	time_start = utime.time()

	while(utime.time() - time_start < 20):
			print(".",end="")
			status = gsm.status()

			if (status[0] == 89):
				connection = True
				return connection

			time.sleep(0.5)

	return connection


def setup_gsm_clock():
	gsm_clock = False

	gsm.atcmd('AT+CLTS=1') # enable gsm RTC time sync
	gsm.atcmd('AT+COPS=2') # unregister from network
	time.sleep(3)
	gsm.atcmd('AT+COPS=0') # register to network (needed for AT+CLTS to take effect)

	reregister_time = utime.time()

	while(utime.time() - reregister_time < 20):
		gsm_clock = gsm.atcmd('AT+COPS?', printable=True)
		
		if (gsm_clock[9:12] == '0,0'):
			gsm_clock = True
			return gsm_clock

		print(".", end="")
		time.sleep(1)

	return gsm_clock


def read_gsm_clock():
	return gsm.atcmd("AT+CCLK?", printable=True)


def net_quality():
	net_quality = gsm.atcmd('AT+CSQ', printable=True)
	spl = net_quality.split(" ")
	res = int(spl[1].split(",")[0])

	if (res < 0 or res > 31): # valid values are 0-31
		return "--"
	return round(res * 100 / 31)


def status_sms(ADMIN_NUMBERS, boot_at):
	indexes = gsm.checkSMS(status=gsm.SMS_UNREAD)

	if(indexes):
		if (len(indexes) > 0):
			for i in range(1,len(indexes)+1):
				msg = gsm.readSMS(i, True)
				if (msg[2] in ADMIN_NUMBERS):
					if (msg[6] == 'STATUS'):
						text = "Boot: {}, NQ: {}%".format(last_boot(boot_at), net_quality())
						gsm.sendSMS(msg[2], text)
					elif (msg[6] == 'REBOOT'):
						text = "Rebooting..."
						gsm.sendSMS(msg[2], text)
						time.sleep(2)
						machine.reset()


def last_boot(boot_at):
	try:
		part = boot_at.split(" ")[1]
		dt = part.split("+")[0]
		return dt[1:].replace(",", " ")
	except:
		return "n/a"


def call_gate(GATE_NUMBER):
	gsm.atcmd("ATD+ {};".format(GATE_NUMBER)) #call the gate number    
	call_time = utime.time()

	while(utime.time() - call_time < 15):
		net_state = gsm.atcmd('AT+CLCC', printable=True)
		try:
			if (net_state[13] in ['2', '3']): # if the state is 'dialing' or 'ringing'
				print(".", end="")
				time.sleep(0.5)
			else:
				gsm.atcmd("ATH") # hang up just to be safe
				break
		except:
			pass

	gsm.atcmd("ATH")
	print("\n")


def loop(VALID_NUMBERS, ADMIN_NUMBERS, GATE_NUMBER, boot_at):
	loop_index = 0

	print("\nWaiting for incomming calls...")

	while(gsm.atcmd('AT+CREG?', printable=True).split(" ")[1][2] == '1'):
		caller_id = gsm.atcmd('AT+CLCC', printable=True) # includes callers phone number in case of incomming call
		incomming_call = False
		try:		
			if (caller_id == '..OK..'): #listening to network, no incomming/outgoing calls
				pass
			elif (caller_id[13] == '4' and len(caller_id) > 32): #incomming call
				incomming_call = True
		except:
			machine.reset()

		if (incomming_call):
			gsm.atcmd('ATH') #hangup

			caller_number = caller_id[20:32] # phone number extraction

			print("\nIncomming call from: {}".format(caller_number))

			if (caller_number in VALID_NUMBERS):
				print('\nNumber is valid. Calling {}...'.format(GATE_NUMBER))
				call_gate(GATE_NUMBER)
			else:
				print('Number is invalid.\n')
				#do nothing

		if (loop_index >= 5): # check sms every 5 loops (~5 secs)
			status_sms(ADMIN_NUMBERS, boot_at)
			loop_index = 0

		loop_index += 1
		print("*", end="")
		time.sleep(1)

	machine.reset() # if the while loop ended it means we are no longer connected - reboot