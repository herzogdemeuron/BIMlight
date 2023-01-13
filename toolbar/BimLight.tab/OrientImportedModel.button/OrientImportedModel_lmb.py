import hdmrhino as hdm
import rhinoscriptsyntax as rs
import os
# Source
point_A = rs.CreatePoint(155398,83666.9,408.7)
point_B = rs.CreatePoint(1668.43,9987,0)
Rotation = -19.53 # Degrees
# Run
hdm.project547.OrientImportedModel(point_A,point_B,Rotation)

#Rhino Toolbar Counter
hdm.button_count(os.getcwd(), "Orient Imported Model")