import bimlight
import rhyton

rhyton.Rhyton(bimlight.BIMLIGHT)
rhyton.Powerbi.update()
bimlight.Log('Push to PowerBI')