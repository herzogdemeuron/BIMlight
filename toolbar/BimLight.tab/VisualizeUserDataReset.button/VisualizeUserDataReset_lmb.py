import hdmrhino as hdm
import os

hdm.visualize.VisualizeUserDataReset()
#old click counter
#hdm.count_click("VisualizeUserDataReset")

#Rhino Toolbar Counter
hdm.button_count(os.getcwd(), "Reset Information Visualization")