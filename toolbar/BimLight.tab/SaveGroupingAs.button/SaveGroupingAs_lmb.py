import hdmrhino as hdm
import os

hdm.grouping.SaveGroupingAs()
#old click counter
#hdm.count_click("SaveGroupingAs")

#Rhino Toolbar Counter
hdm.button_count(os.getcwd(), "Save Grouping")