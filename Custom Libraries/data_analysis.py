#!/usr/bin/env python3

"""Bokeh data visualization.

This module uses Bokeh v.0.12.12 to perform an interactive analysis on data, from a set of 
various techniques. The purpose is to encourage statistical process control (SPC).

Arguments:
    argv[1]: config json file path
    
ToDo:
    ~~~~NOW~~~~
    ~~~~CONSIDERATION~~~~
    ~~~~PERIODICALLY~~~~
    improve docstrings
    improve modularity (globals, fxns, variables)
    improve naming
    return vs return None vs nothing
    
"""

#~~~~  IMPORTS  ~~~~#
import tools
import variation_analysis

#~~~~  PRIVATE GLOBAL VARIABLES  ~~~~#
# script arguments for testing/development
_TEST_ARGV1 = r"C:\Users\Alfred\Documents\GitHub\Python\Custom Libraries\test_config.json"
_TEST_ARGV2 = r"C:\Users\Alfred\Documents\GitHub\Python\Custom Libraries\test_log.log"

#~~~~  PUBLIC GLOBAL VARIABLES  ~~~~#

#~~~~  PRIVATE CLASSES  ~~~~#

#~~~~  PUBLIC CLASSES  ~~~~#

#~~~~  PRIVATE FUNCTIONS  ~~~~#

#~~~~  PUBLIC FUNCTIONS  ~~~~#

#~~~~  MAIN  ~~~~#
def main():
    variation_analysis.variation_analysis(json_file_path=_TEST_ARGV1)

main()


#~~~~  DEAD CODE  ~~~~#

# def main():
#     function_flag = 0
#     if(function_flag is 0):
#         # donald wheeler's variation analysis
#         
#         # DISPLAY ALL SCRIPT ARGUMENTS
#         print(tools.make_formatted_title("script arguments"))
#         print(tools.make_formatted_script_args())
#         
#         # PARSE EXCEL, ANALYZE DATA, AND MAKE UI
#         print(tools.make_formatted_title("parse/process all data subsets"))
#         # create UI
#         #@DEBUG
#         display_column_of_rows = []
#         # display_subset = create_UI(_prepare_variation_analysis_data(sys.argv[1]), sys.argv[2])
#         display_subset = create_UI(_prepare_variation_analysis_data(_TEST_ARGV1), _TEST_ARGV2)
#         # display_column_of_rows.append(display_subset)
#         # # DISPLAY ONTO WEB BROWSER
#         # bkio.curdoc().add_root(display_column_of_rows)
#         
#         #@old
#         # init bokeh & track UI components       
#         # subprocess.run(["bokeh.exe", "serve", "--show"], shell=True)
#         # session = bkc.push_session(bkio.curdoc()) 
#         # 
#         # display_column_of_rows = []
#         # _get multi-column data groups sequentially
#         # for sources in get_data_subsets(sys.argv[1], sys.argv[2]):
#         #     # create UI subset
#         #     display_subset = create_UI(sources, sys.argv[3])
#         #     
#         #     # add to final UI superset
#         #     display_column_of_rows.append(display_subset)
#         #     
#         # # DISPLAY ONTO WEB BROWSER
#         # bkio.curdoc().add_root(bkl.column(display_column_of_rows))
#         # 
#         
#         # bkio.show(bkio.curdoc(), browser="chrome")
#         
#         # session.loop_until_closed()
#         
#         None
#     elif(function_flag is 1):
#         # placeholder
#         None
#     elif(function_flag is 2):
#         # placeholder
#         None