import hdmrhino as hdm
import os

hdm.grouping.AssignGroupColor()
#old click counter
#hdm.count_click("AssignGroupColor")

#Rhino Toolbar Counter
hdm.button_count(os.getcwd(), "Assign Grouping Color")