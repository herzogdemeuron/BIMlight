import hdmrhino as hdm
import os

hdm.visualize.VisualizeUserDataBySum()
#old click counter
#hdm.count_click("VisualizeUserDataBySum")

#Rhino Toolbar Counter
hdm.button_count(os.getcwd(), "Visualize Data Sum")