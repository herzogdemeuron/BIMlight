import bimlight
import rhyton

rhyton.Rhyton(bimlight.BIMLIGHT)
rhyton.Visualize.reset(clearSource=True)
bimlight.Log('Visualize User Data Reset')