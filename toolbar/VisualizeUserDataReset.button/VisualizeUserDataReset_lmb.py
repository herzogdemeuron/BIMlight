import bimlight
import rhyton

rhyton.Rhyton(bimlight.BIMLIGHT)
rhyton.Visualize.reset()
bimlight.Log('Visualize User Data Reset')