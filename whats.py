import pyautogui
import time

import schedule


# Specify the phone number (with country code) and the message
phone_number = "7075297736"
message = "Good morning ."

# Open the Start menu
pyautogui.press('win')
time.sleep(1)

# Type "WhatsApp"
pyautogui.write('WhatsApp', interval=0.1)
time.sleep(1)

# Press Enter to open WhatsApp
pyautogui.press('enter')
time.sleep(5)  # Wait for WhatsApp to open

# Click on the search bar in WhatsApp
pyautogui.hotkey('ctrl', 'f')
time.sleep(1)

# Type the phone number
pyautogui.write(phone_number, interval=0.1)
time.sleep(2)
pyautogui.press('down')

# Press Enter to select the contact
pyautogui.press('enter')
time.sleep(2)

# Type the message
for i in range(5):
    pyautogui.write(message, interval=0.1)

    pyautogui.press('enter')
    # time.sleep(1)
for i in range(4):
    pyautogui.write("All the best for your exam.", interval=0.1)
    pyautogui.press('enter')
schedule.every().day.at("11:00").do(message)
# Press Enter to send the message
# import sys
# print(sys.executable)