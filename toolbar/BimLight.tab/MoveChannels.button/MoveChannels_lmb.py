import hdmrhino as hdm
import rhinoscriptsyntax as rs
import sys

channels = ['_objectId', '_depth', '_materialId']
folder = rs.BrowseForFolder()

if not folder:
    sys.exit()

hdm.project547.MoveChannels(folder, channels)
hdm.count_click("RemoveChannels")