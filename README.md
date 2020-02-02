# Custom gsm gate control solution

This is a custom solution to a specific problem. Feel free to use the code as an idea or a template if you find yourself in a similar situation.

If you have a barrier gate that is opened by a phone call and (for whatever reason) you don't want to/can't register more than one number, but want to control it with more than one phone - this can be used as a starting point for your own custom solution. This is a hobby project, use at your own risk.

# Requires:
- ESP32 board (e.x. LILYGO® TTGO T-Call V1.3 ESP32)
- Micropython with gsm module enabled. [Get it here](https://github.com/Xinyuan-LilyGO/TTGO-T-Call/tree/master/examples/MicroPython_LoBo)
- SIM800L (or any equivalent)
- 2G enabled SIM card (disable PIN code first)

# How does it work?

- Register your 2G SIM cards number at the barrier gate you want to control
- Add all the numbers you want to be able to control the gate with to a list called "VALID_NUMBERS" (you can add as many as you want until you run out of memory)
- Add all the numbers you want to have SMS control ability to "ADMIN_NUMBERS" list
- When the device receives an incomming call it hangs it up, checks if it's within the list of valid numbers (VALID_NUMBERS) and if yes - calls the gate to open it.
- Accepts SMS controls from a list of admin numbers (ADMIN_NUMBERS). Possible commands are "STATUS" (returns last boot time and current network quality in %) and "REBOOT" (reboots the device).