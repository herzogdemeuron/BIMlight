import hdmrhino as hdm
import os


hdm.settings.SettingsBimLight()
#old click counter
#hdm.count_click("SettingsBimLight")

#Rhino Toolbar Counter
hdm.button_count(os.getcwd(), "BIM Light Settings")