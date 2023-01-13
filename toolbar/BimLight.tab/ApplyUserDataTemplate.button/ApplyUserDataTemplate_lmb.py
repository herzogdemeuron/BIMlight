import hdmrhino as hdm
import os

hdm.ApplyUserDataJsonTemplate()

# TO BE MOVED TO DEV
# Rhino Toolbar Counter
hdm.button_count(os.getcwd(), "Apply User Data Template")