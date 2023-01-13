import hdmrhino as hdm
import os

hdm.grouping.RenameGroup()
#old click counter
#hdm.count_click("RenameGroup")

#Rhino Toolbar Counter
hdm.button_count(os.getcwd(), "Rename Grouping")