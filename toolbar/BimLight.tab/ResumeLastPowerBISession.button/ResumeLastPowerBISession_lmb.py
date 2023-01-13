import hdmrhino as hdm
import os

hdm.powerbi.ResumeLastPowerBISession()
#old click counter
#hdm.count_click("ResumeLastPowerBISession")

#Rhino Toolbar Counter
hdm.button_count(os.getcwd(), "Resume Last PowerBI Session")