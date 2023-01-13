import hdmrhino as hdm
import os

hdm.visualize.VisualizeUserDataByGrouping()
#old click counter
#hdm.count_click("VisualizeUserDataByGrouping")

#Rhino Toolbar Counter
hdm.button_count(os.getcwd(), "Visualize Data by Grouping")