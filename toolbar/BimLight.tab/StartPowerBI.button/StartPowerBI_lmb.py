import hdmrhino as hdm
import os

hdm.powerbi.StartPowerBI()
#old click counter
#hdm.count_click("StartPowerBI")

#Rhino Toolbar Counter
hdm.button_count(os.getcwd(), "Start PowerBI")