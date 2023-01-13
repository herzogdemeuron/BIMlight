import hdmrhino as hdm
import os

hdm.calculate.CreateObjectInformation(True)
#old click counter
#hdm.count_click("CreateObjectInformationGeometry")

#Rhino Toolbar Counter
hdm.button_count(os.getcwd(), "Calculate Information and Display")
