# -*- coding: utf-8 -*-

'''
     __  __     _____     __    __           _____     ______
    /\ \_\ \   /\  __-.  /\ \-./  \         /\  __-.  /\__  _\
    \ \  __ \  \ \ \/\ \ \ \ \-./\ \        \ \ \/\ \ \/_/\ \/
     \ \_\ \_\  \ \____-  \ \_\ \ \_\        \ \____-    \ \_\
      \/_/\/_/   \/____/   \/_/  \/_/         \/____/     \/_/

    BIMlight - PowerBI

    Created on 29. June 2022 by j.hoell, y.schindel

'''

##------------------ IMPORTS
import rhinoscriptsyntax as rs
from datetime import datetime
import os
import os.path as op
import csv
import shutil # standard module to copy a file
from variablesbl import *
from utilsbl import *
from export import ExportUserData

##------------------ PUBLIC FUNCITONS


def StartPowerBI():
    """
    Starts a fresh PowerBI live session, overwrites data from previous sessions.

    """
    # check if PowerBI is aready running
    # if so, stop don't open a second instance
    power_bi_running = process_exists('PBIDesktop.exe')
    if power_bi_running:
        rs.MessageBox(
        """
        PowerBI is already running.

        Option 1: Close current session and start a new one
        
        Option 2: Use the 'Update PowerBI' button to push updates 
        to the current session.""", 
                0, MSG_PREFIX)
        return

    # ask user to select a template
    template_chosen = rs.ListBox(PBI_TEMPLATE_OPTIONS, "Choose a PowerBI template:", 
                                MSG_PREFIX, default=0)
    template = None
    custom_template = False

    if not template_chosen:
        return
    if template_chosen == PBI_TEMPLATE_1_ALIAS:
        template = PBI_TEMPLATE_1
    elif template_chosen == PBI_TEMPLATE_2_ALIAS:
        template = PBI_TEMPLATE_2
    elif template_chosen == PBI_TEMPLATE_3_ALIAS:
        template = PBI_TEMPLATE_3
    elif template_chosen == PBI_TEMPLATE_CUSTOM_ALIAS:
        template = rs.OpenFileName("Open", "PowerBI Template (*.pbit)|*.pbit||")
        custom_template = True
    
    # write the current PowerBI mode into document text for correct updating procedure
    rs.SetDocumentUserText(PBI_MODE, template_chosen)

    # csv file path
    csv_path = prepare_file_path(PBI_DATA_NAME, EXPORT_PATH)

    # check for old csv file
    if op.exists(csv_path):
        overwite = rs.MessageBox("Overwriting data from previous session", 1 | 64, MSG_PREFIX)
        if overwite == 2:
            return
    else:
        print("INFO: No data from previous session was found.")

    # export data, returns False if process was cancelled by user
    start_power_bi = False

    if template == PBI_TEMPLATE_2:
        start_power_bi = ExportUserData(file_path=csv_path,
                            open_export_file=False,
                            get_user_input=False,
                            no_hierarchy=True,
                            power_bi=True)
    elif template == PBI_TEMPLATE_1 or template == PBI_TEMPLATE_3:
        start_power_bi = ExportUserData(file_path=csv_path,
                            open_export_file=False,
                            get_user_input=False,
                            max_hierarchy=MAX_HIERARCHY,
                            power_bi=True)
    elif custom_template:
        start_power_bi = ExportUserData(file_path=csv_path,
                            open_export_file=False,
                            get_user_input=True,
                            power_bi=True)

    # Start PowerBI using a template file
    if os.path.exists(template):
        print("Downloading PowerBI template from server...")
        shutil.copyfile(template, PBI_TEMPLATE_LOCAL)
        if os.path.exists(PBI_TEMPLATE_LOCAL):
            if start_power_bi != False:
                try:
                    os.startfile(PBI_TEMPLATE_LOCAL)
                    print("Starting new PowerBI session...")
                except:
                    rs.MessageBox(("""Could not start PowerBI,
                                    install 'PowerBI Desktop' from Microsoft Store, or contact DT"""), 0 | 16, MSG_PREFIX)
            else:
                print("PowerBI startup cancelled.")
        else:
            rs.MessageBox(("Could not download PowerBI template, contact DT"), 0 | 16, MSG_PREFIX)
    else:
        rs.MessageBox(("No PowerBI template found on server, contact DT"), 0 | 16, MSG_PREFIX)
    return


def PushToPowerBI():
    '''
    Appends a new batch of data to the exchange csv.

    '''
    # Known limitations:
    # If the files has remembered an export setting including a parameter 
    # that is not shared by all objects -
    # Next, PowerBI is startet without those special objects selected.
    # PushToPowerBI is then executed with those special object included.
    # This will create a csv file with entries that are in the wrong column.
    
    # check if PowerBI is aready running
    # if so, stop don't open a second instance
    power_bi_running = process_exists('PBIDesktop.exe')
    if not power_bi_running:
        rs.MessageBox("No active PowerBI session, resume previous or start a new one.", 
                0 | 64, MSG_PREFIX)
        return

    # csv file path
    csv_path = prepare_file_path(PBI_DATA_NAME, EXPORT_PATH)

    # check for old csv file
    if os.path.exists(csv_path):
        print("INFO: Appending new data to previous data...")
    else:
        rs.MessageBox(("""Data transfer file is missing. 
                        Close PowerBI and start a new session.
                        If problem persists, contact DT"""), 0, MSG_PREFIX)
        return

    # get PowerBI mode from document user text and 
    # configure argument for ExportUserData
    append_file = False
    max_hier = False
    no_hier = False
    pbi_mode = rs.GetDocumentUserText(PBI_MODE)

    if pbi_mode == PBI_TEMPLATE_1_ALIAS:
        append_file = False
    elif pbi_mode == PBI_TEMPLATE_2_ALIAS or pbi_mode == PBI_TEMPLATE_3_ALIAS:
        append_file = True
    elif pbi_mode == PBI_TEMPLATE_CUSTOM_ALIAS:
        append_file = False
        max_hier = False
        no_hier = False
        
    if pbi_mode == PBI_TEMPLATE_2_ALIAS:
        max_hier = False
        no_hier = True
    elif pbi_mode == PBI_TEMPLATE_1_ALIAS or pbi_mode == PBI_TEMPLATE_3_ALIAS:
        max_hier = MAX_HIERARCHY
        no_hier = False

    # export data in previously specified append or override mode,
    # don't open export file
    update_success = None
    update_success = ExportUserData(file_path=csv_path, 
                        append_existing_file=append_file, 
                        open_export_file=False,
                        get_user_input=False,
                        no_hierarchy=no_hier,
                        max_hierarchy=max_hier,
                        power_bi=True)
    print(update_success)
    if update_success == None:
        rs.MessageBox("Update Successful!", 0 | 48, MSG_PREFIX)
        return
    else:
        print("Update cancelled")
        return


def ResumeLastPowerBISession():
    """
    Opens powerBI without overriting previously exported data. This let's you continiue with the dataset exported last.
    """
    # check if PowerBI is aready running
    # if so, stop don't open a second instance
    power_bi_running = process_exists('PBIDesktop.exe')
    if power_bi_running:
        rs.MessageBox(
        """
        PowerBI is already running.

        Option 1: Close current session and start a new one
        
        Option 2: Use the 'Update PowerBI' button to push updates 
        to the current session.""", 
                0, MSG_PREFIX)
        return

    # open local file
    if os.path.exists(PBI_TEMPLATE_LOCAL):
        try:
            os.startfile(PBI_TEMPLATE_LOCAL)
            print("Resuming last PowerBI session...")
        except:
            rs.MessageBox(("Could not start PowerBI, contact DT"), 0 | 16, MSG_PREFIX)
    else:
        rs.MessageBox(("No local PowerBI template found. Start a new PowerBI session."), 0 | 16, MSG_PREFIX)

    return


def DeleteLastPowerBIUpdate():
    """
    Deletes the last model update from the exchange csv. Can be used multiple times.
    """
    # csv file path
    csv_path = prepare_file_path(PBI_DATA_NAME, EXPORT_PATH)

    # check for old csv file
    if os.path.exists(csv_path):
        user_confirmed = rs.MessageBox("Are you sure about that?", 1 | 0, MSG_PREFIX)
        if user_confirmed == 1:
            print("INFO: Deleting last data push...")
            with open(csv_path, 'r') as csv_file:
                reader = csv.reader(csv_file, delimiter = ';')
                headers = next(reader, None)
                position = headers.index('date_time')
                # read lines, remove (strip) '\n' and split string into list 
                data = [line.strip().split(';') for line in csv_file.readlines()]

            # get item in last sublist - is the last update -
            if len(data) > 1:
                last_update = data[-1][position]
            else:
                print("There are no updates to remove...")

            data_new = []
            # remove last update from data
            for index, item in enumerate(data):
                if last_update not in item:
                    data_new.append(item)

            # open file again and write all remaining data into cleared file
            with open(csv_path, 'wb') as csv_file:
                writer = csv.writer(csv_file,  delimiter = ';')
                data_new.insert(0, headers)
                writer.writerows(data_new)
                if len(data) > 1:
                    rs.MessageBox("Successfully removed last update", 0, MSG_PREFIX)
        else:
            return
    else:
        rs.MessageBox(("""Data transfer file is missing. 
                        Close PowerBI and start a new session.
                        If problem persists, contact DT"""), 0, MSG_PREFIX)
        return
    return

