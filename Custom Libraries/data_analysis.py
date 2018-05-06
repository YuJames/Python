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
import functools
import tools
import tkinter as tk
import tkinter.messagebox as tkm
import tkinter.filedialog as tkf
import variation_analysis

#~~~~  PRIVATE GLOBAL VARIABLES  ~~~~#
# script arguments for testing/development
_TEST_ARGV1 = r"C:\Users\Alfred\Documents\GitHub\Python\Custom Libraries\test_config.json"
_TEST_ARGV2 = r"C:\Users\Alfred\Documents\GitHub\Python\Custom Libraries\test_log.log"

#~~~~  PUBLIC GLOBAL VARIABLES  ~~~~#

#~~~~  PRIVATE CLASSES  ~~~~#
class _UI():
    def __init__(self, parent):
        # metadata
        parent.title("Data Analysis Script")
        self.frame1 = tk.Frame(parent, bg="blue", padx=20, pady=30)
        self.frame1.pack(fill=tk.BOTH, expand=True)
        #root.geometry('350x200')
        
        # file widgets
        self.json_title = tk.Label(self.frame1, text="JSON Config File")
        self.json_title.grid(column=0, row=0)
        self.json_path = tk.Entry(self.frame1, width=30)
        self.json_path.focus()
        self.json_path.grid(column=1, row=0)
        self.json_search = tk.Button(self.frame1, text="browse", command=functools.partial(self._cb_file, widget=self.json_path))
        self.json_search.grid(column=2, row=0)        
        
        excel_title = tk.Label(self.frame1, text="Excel Data File")
        excel_title.grid(column=0, row=1)
        excel_path = tk.Entry(self.frame1, width=30)
        excel_path.grid(column=1, row=1)
        excel_search = tk.Button(self.frame1, text="browse", command=functools.partial(self._cb_file, widget=excel_path))
        excel_search.grid(column=2, row=1)
    
        log_title = tk.Label(self.frame1, text="Log File")
        log_title.grid(column=0, row=2)
        log_path = tk.Entry(self.frame1, width=30)
        log_path.grid(column=1, row=2)
        log_search = tk.Button(self.frame1, text="browse", command=functools.partial(self._cb_file, widget=log_path))
        log_search.grid(column=2, row=2)
        
        # menu widgets
        self.menu = tk.Menu(parent)
        parent.config(menu=self.menu)
        
        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.file_menu.add_command(label="Save")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Open")
        self.menu.add_cascade(label="File", menu=self.file_menu)
        
        # misc widgets
        self.options = tk.Checkbutton(self.frame1, text="option 1", command=self._cb_popup)
        self.options.grid(column=4, row=0)
        
        
    def _cb_file(self, widget):
        file = tkf.askopenfilename()
        widget.delete(0, "end")
        widget.insert(0, file)
    
    def _cb_popup(self):
        tkm.showinfo("title", "content")
        # showerror, showwarning
        
#~~~~  PUBLIC CLASSES  ~~~~#

#~~~~  PRIVATE FUNCTIONS  ~~~~#

#~~~~  PUBLIC FUNCTIONS  ~~~~#

#~~~~  MAIN  ~~~~#
def main():
    root = tk.Tk()
    gui = _UI(root)
    root.mainloop()
    
    # variation_analysis.variation_analysis(json_file_path=_TEST_ARGV1)

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