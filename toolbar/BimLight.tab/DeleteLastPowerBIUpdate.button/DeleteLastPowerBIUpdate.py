import hdmrhino as hdm
import os

hdm.powerbi.DeleteLastPowerBIUpdate()
#old click counter
#hdm.count_click("DeleteLastPowerBIUpdate")

#Rhino Toolbar Counter
hdm.button_count(os.getcwd(), "Undo Last PowerBI Update")