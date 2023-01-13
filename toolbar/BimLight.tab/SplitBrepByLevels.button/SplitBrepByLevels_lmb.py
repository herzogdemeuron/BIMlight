import hdmrhino as hdm
import os

hdm.calculate.SplitBrepByLevels()
#old click counter
#hdm.count_click("SplitBrepByLevels DEV")

#Rhino Toolbar Counter
hdm.button_count(os.getcwd(), "Split Brep by Levels")