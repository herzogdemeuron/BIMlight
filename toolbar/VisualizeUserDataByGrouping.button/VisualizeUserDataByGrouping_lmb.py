import bimlight
import rhyton

rhyton.Rhyton(bimlight.BIMLIGHT)
rhyton.Visualize.byGroup()
bimlight.Log('Visualize User Data by Grouping')