import hdmrhino as hdm
import os

hdm.powerbi.PushToPowerBI()
#old click counter
#hdm.count_click("PushToPowerBI")

#Rhino Toolbar Counter
hdm.button_count(os.getcwd(), "Update PowerBI")