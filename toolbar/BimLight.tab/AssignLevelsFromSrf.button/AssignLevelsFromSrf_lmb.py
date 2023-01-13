import hdmrhino as hdm
import os

hdm.calculate.AssignLevelsFromSrf()
#old click counter
#hdm.count_click("AssignLevel")

#Rhino Toolbar Counter
hdm.button_count(os.getcwd(), "Assign Level")
