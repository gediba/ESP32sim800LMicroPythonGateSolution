import gsm
import machine
from machine import Pin

from func import *

led_pin = Pin(13, Pin.OUT) # blue onboard led
led_pin.value(0)

VALID_NUMBERS = ['+XXXxxxxxxxx', '+XXXxxxxxxxx']
ADMIN_NUMBERS = ['+XXXxxxxxxxx'] # sms commands work for these numbers only
GATE_NUMBER = '+XXXxxxxxxxx'

gsm_module_power()

print("Attempting to connect to GSM network.")

connection = gsm_start(led_pin)

if not connection:
	print("\nFailed to connect to gsm network. Restarting...\n")
	machine.reset()

led_pin.value(1)

print("\nConnected to GSM network.")
print("Signal quality is: {}%".format(net_quality()))
print("Setting time...")

gsm_clock = setup_gsm_clock()

if not gsm_clock:
	print("Failed to set network time. Resetting...")
	machine.reset()

print('OK')
boot_at = read_gsm_clock()

loop(VALID_NUMBERS, ADMIN_NUMBERS, GATE_NUMBER, boot_at)

