import hdmrhino as hdm
import os

hdm.export.ExportUserData()
#old click counter
#hdm.count_click("ExportUserData")

#Rhino Toolbar Counter
hdm.button_count(os.getcwd(), "Export Data")