import hdmrhino as hdm
import os

hdm.CreateUserDataJsonTemplate()

# TO BE MOVED TO DEV
# Rhino Toolbar Counter
hdm.button_count(os.getcwd(), "Create User Data Template")