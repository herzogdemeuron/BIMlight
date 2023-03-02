import bimlight
import rhyton

rhyton.Settings('bimlight').saveSettings(
        keyPrefix=bimlight.BL_PREFIX,
        unitSuffix='FT',
        roundingDecimals=5)

# bimlight.settings.SettingsBimLight()
bimlight.Log('Settings Bimlight')