import hdmrhino as hdm
import os

hdm.calculate.CreateObjectInformation()
#old click counter
#hdm.count_click("CreateObjectInformation")

#Rhino Toolbar Counter
hdm.button_count(os.getcwd(), "Calculate Information")
