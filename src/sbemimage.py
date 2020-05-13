#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#==============================================================================
#   SBEMimage, ver. 2.0
#   Acquisition control software for serial block-face electron microscopy
#   (c) 2016-2018 Benjamin Titze,
#   Friedrich Miescher Institute for Biomedical Research, Basel.
#   This software is licensed under the terms of the MIT License.
#   See LICENSE.txt in the project root folder.
#==============================================================================

"""SBEMimage.py launches the application.
   Use 'python SBEMimage.py' or call the batch file SBEMimage.bat.
"""

import os
import sys
# import ctypes
from configparser import ConfigParser
from PyQt5.QtWidgets import QApplication
import colorama # needed to suppress TIFFReadDirectory warnings in the console

from dlg_windows import ConfigDlg
from config_template import process_cfg
from main_controls import MainControls

VERSION = '2.0 (R2018-07-07)'

def main():
    """Load configuration and run QApplication.
    Let user select configuration file. Preselect the configuration from the
    previous run (saved in status.dat), otherwise default.ini.
    Quit if default.ini can't be found.
    Check if configuration can be loaded and if it's compatible with the
    current version of SBEMimage. If not, quit.
    """
    SBEMimage = QApplication(sys.argv)
    app_id = 'SBEMimage ' + VERSION
    # ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    colorama.init()
    os.system('cls')
    os.system('title SBEMimage - Console')
    print('***********************************\n'
          '     SBEMimage\n'
          '     Version %s\n'
          '***********************************\n' % VERSION)

    configuration_loaded = False
    default_configuration = False

    cfg_dir = os.path.join('..','cfg')

    if (os.path.isfile(os.path.join(cfg_dir, 'default.ini'))
            and os.path.isfile(os.path.join(cfg_dir, 'system.cfg'))):
        # Ask user to select .ini file:
        startup_dialog = ConfigDlg(VERSION)
        startup_dialog.exec_()
        dlg_response = startup_dialog.get_ini_file()
        if dlg_response == 'abort':
            configuration_loaded = False
            print('Program aborted by user.\n')
            sys.exit()
        else:
            try:
                config_file = dlg_response
                if config_file == 'default.ini':
                    default_configuration = True
                print('Loading configuration file %s ...'
                      % config_file, end='')
                config = ConfigParser()
                with open(os.path.join(cfg_dir, config_file), 'r') as file:
                    config.read_file(file)
                print(' Done.\n')
                # Load corresponding system settings file
                sysconfig_file = config['sys']['sys_config_file']
                if default_configuration and sysconfig_file != 'system.cfg':
                    sysconfig_file = 'system.cfg'
                    config['sys']['sys_config_file'] = 'system.cfg'
                print('Loading system settings file %s ...'
                      % sysconfig_file, end='')
                sysconfig = ConfigParser()
                with open(os.path.join(cfg_dir, sysconfig_file), 'r') as file:
                    sysconfig.read_file(file)
                configuration_loaded = True
                print(' Done.\n')
            except:
                configuration_loaded = False
                print('\nError while loading configuration! Program aborted.\n')
                # Keep terminal window open when run from batch file
                os.system('cmd /k')
                sys.exit()
    else:
        # Quit if default.ini doesn't exist
        configuration_loaded = False
        print('Error: default.ini and/or system.cfg not found. '
              'Program aborted.\n')
        os.system('cmd /k')
        sys.exit()

    if configuration_loaded:
        # Check selected .ini file and ensure there are no missing entries.
        # Configuration must match template configuration in default.ini.
        if default_configuration:
            # Check only if number of entries correct
            success, _, _, _ = process_cfg(config, sysconfig, True)
        else:
            # Check and update if necessary
            success, changes, config, sysconfig = process_cfg(config, sysconfig)

        if success:
            if default_configuration:
                print('Default configuration loaded.\n')
            else:
                if changes[0] and changes[1]:
                    ch_str = 'config and sysconfig updated'
                elif changes[0]:
                    ch_str = 'config updated'
                elif changes[1]:
                    ch_str = "sysconfig updated"
                else:
                    ch_str = 'complete, no updates'
                print('Configuration loaded and checked: ' + ch_str + '\n')
            # Remove status file. It will be recreated when program terminates
            # normally.
            if os.path.isfile(os.path.join(cfg_dir, 'status.dat')):
                os.remove(os.path.join(cfg_dir, 'status.dat'))
            print('Initializing SBEMimage. Please wait...\n')
            # Launch Main Controls. Viewport is launched from Main Controls.
            SBEMimage_main_window = MainControls(config,
                                                 sysconfig,
                                                 config_file,
                                                 VERSION)
            sys.exit(SBEMimage.exec_())
        else:
            print('Error while validating configuration file(s). '
                  'Program aborted.\n')
            os.system('cmd /k')
            sys.exit()

if __name__ == '__main__':
    main()
