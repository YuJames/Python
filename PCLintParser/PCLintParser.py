#!/usr/bin/env python3

"""PCLint output filter.

This module uses regex to search the output of PCLint for target info. The purpose is to encourage
better coding practices.

Arguments:
    argv[1]: PCLint output file path

ToDo:
    ~~~~NOW~~~~
    ~~~~CONSIDERATION~~~~
    ~~~~PERIODICALLY~~~~
"""

#~~~~  IMPORTS  ~~~~#
import os
import re
import sys

#~~~~  PRIVATE GLOBAL VARIABLES  ~~~~#
_dave_files = ("ADC0.C", "ADC1.C", "CAN.C", "CC2.C", "GPT1.C", "GPT2.C", "IO.C", "RTD_ARINC_U1C0.C",
               "SCS.C", "U0C0.C", "U1C0.C", "U2C1.C", "USIC0.C", "USIC1.C", "USIC2.C", "WDT.C",
               "MAIN.C", "Start_V3.A66")
_npd_files = ("CMT_MSG_Chiller.h", "CMT_MSG_Definitions.h", "NPD_ApplSw_API.h", "NPD_CanApplIntf.h",
             "NPD_CanPinProg.h", "NPD_ErrCodes.h", "NPD_Events.h", "NPD_Events.h", 
             "NPD_Initialize.h", "NPD_NvmLayout.h", "NPD_SysConst.h", "NPD_SysVars.h", "Types.h", 
             "UniversalIO.h", "CDB_Defs.h", "CDL_CanDevice.h", "NCN_CanQueue.c", "NCN_CanQueue.h", 
             "NCN_CanService.c", "NCN_CanService.h", "NDI_Diags.c", "NDI_Diags.h", 
             "NDL_NvmDevice.h", "NDT_DataTransfer.c", "NDT_DataTransfer.h", "NPC_PowerControl.c", 
             "NPC_PowerControl.h", "NPD_Arinc825Defs.c", "NPD_Arinc825Defs.h", "NPD_CanSysMsgs.h", 
             "NPD_Events.c", "NPD_Initialize.c", "NPD_MainService.c", "NPD_MainService.h", 
             "NPD_NvmLayout.c", "NPD_Properties.c", "NPD_Properties.h", "NPD_SysVars.c", 
             "NPD_Timers.c", "NPD_Timers.h", "NSR_NpdMessages.c", "NSR_NpdMessages.h", 
             "NSR_SerDevice.c", "SR_SerDevice.h", "NSR_SerMessage.h", "NTM_NetMonitor.c", 
             "NTM_NetMonitor.h", "NTM_NocNetMon.c", "NTM_NocNetMon.h", "NVM_Device.c", 
             "NVM_Device.h", "Routine_Hdr.h", "SDL_SerDevice.h")
             
_all_ignore_files = _dave_files + _npd_files

#~~~~  PUBLIC GLOBAL VARIABLES  ~~~~#

#~~~~  PRIVATE CLASSES  ~~~~#

#~~~~  PUBLIC CLASSES  ~~~~#

#~~~~  PRIVATE FUNCTIONS  ~~~~#
def _preprocess_ignores():
    """Preprocess the list of files to ignore.
    
    Args:
        None
    Retuns:
        None
    """
    
    global _all_ignore_files
    
    # filter duplicates
    _all_ignore_files = tuple(set(_all_ignore_files))

    
def _find_target(PCLint_output):
    """Filter and save target info into a new file.
    
    Args:
        PCLint_output: PCLint output to filter (str)
    Returns:
        resulting file path (str)
    """

    target_counter = 0
    info_counter = 0
    error_counter = 0
    warning_counter = 0
    note_counter = 0
    misc_counter = 0
    
    with open(PCLint_output) as f:
        raw = f.read()
        entry_pattern = r"(\"\*\*\*.*?\"|$)"
        error_string = " Error "
        warning_string = " Warning "
        info_string = " Info "
        note_string = " Note "
        
        # from PCLint output, identify all entries
        total_entries = re.findall(pattern=entry_pattern, string=raw, flags=re.DOTALL)

        # from all entries, identify target entries
        target_entries = []
        for entry in total_entries:
            for ignore_file in _all_ignore_files:
                if ignore_file in entry:
                    break
            else:
                target_counter += 1
                target_entries.append(entry)

        # from target entries, identify error, info, warning, note
        for target in target_entries:
            if error_string in target:
                error_counter += 1
            elif warning_string in target:
                warning_counter += 1
            elif info_string in target:
                info_counter += 1
            elif note_string in target:
                note_counter += 1
            else:
                misc_counter += 1
        
        # save results
        new_file_path = os.path.join(os.getcwd(), "result.txt")
        with open(new_file_path, "w") as j:
            for result in target_entries:
                j.write(result + "\n")
    
    # show statistics
    print("~~~STATISTICS~~~")
    print("result: {}".format(new_file_path))
    print("total entries: {}".format(len(total_entries)))
    print("kept entries: {} / {}, {:.2f}%".format(target_counter, len(total_entries), target_counter / len(total_entries) * 100))
    print("error entries: {} / {}, {:.2f}%".format(error_counter, target_counter, error_counter / target_counter * 100))
    print("warning entries: {} / {}, {:.2f}%".format(warning_counter, target_counter, warning_counter / target_counter * 100))
    print("info entries: {} / {}, {:.2f}%".format(info_counter, target_counter, info_counter / target_counter * 100))
    print("note entries: {} / {}, {:.2f}%".format(note_counter, target_counter, note_counter / target_counter * 100))
    print("misc entries: {} / {}, {:.2f}%".format(misc_counter, target_counter, misc_counter / target_counter * 100))
    
    return (new_file_path)

#~~~~  PUBLIC FUNCTIONS  ~~~~#
def main():
    _preprocess_ignores()
    result_file_path = _find_target(sys.argv[1])

#~~~~  MAIN  ~~~~#
if __name__ == "main"
    main()
#~~~~  DEAD CODE  ~~~~#