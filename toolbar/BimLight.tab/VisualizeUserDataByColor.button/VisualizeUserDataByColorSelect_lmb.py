import hdmrhino as hdm
import os


hdm.visualize.VisualizeUserDataByColor(True)
#old click counter
#hdm.count_click("VisualizeUserDataByColorSelect")

#Rhino Toolbar Counter
hdm.button_count(os.getcwd(), "Visualize Data")
