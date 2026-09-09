import bimlight
import rhyton

rhyton.Rhyton(bimlight.BIMLIGHT)
bimlight.exportUserData()
bimlight.Log('Export User Data')
