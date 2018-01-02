#!/usr/bin/env python3

"""Bokeh data visualization.

This module uses Bokeh v.0.12.12 to create interactive web UIs for analyzing 
data. The purpose is to encourage statistical process control (SPC).

Arguments:
    argv[1]: excel file path
    argv[2]: saved data file path
    
ToDo:
    improve table_dict
    Find alternative to globals. Enums?
    change text input value to match closest value (not just if only exceeding max)
        e.g. with y values of [1, 3, 6], a "max y" input of 5 would change to 3
    add more checks/preprocessing?
    fix "float division by zero error" (when sigma = 0)
        impossible? Give warning instead?
    Look into static type checking
        Do not run yet, but prepare code.
    *make sure docstrings are correct
    *improve modularity (globals, fxns, variables)
        review necessity of some functions
    *improve naming
*check consistently throughout project
"""

#~~~~  IMPORTS  ~~~~#
import json  # not currently used
import subprocess # not currently used
import sys
import time  # not currently used

import bokeh
import bokeh.client as bkc
import bokeh.io as bkio
import bokeh.layouts as bkl
import bokeh.models as bkm
import bokeh.models.sources as bkms
import bokeh.models.widgets as bkmw
import bokeh.plotting as bkp
import numpy as np
import pandas as pd
import tools # not currently used

#~~~~  PRIVATE GLOBAL VARIABLES  ~~~~#
# floating precision
_PRECISION = 3
# excel sheet names
_DATA_SHEET_NAME = "Data"
_CONSTANTS_SHEET_NAME = "Constants"
# excel constants
_TITLE_KEY = "title"
_LOWER_LIMIT_KEY = "lower_limit"
_UPPER_LIMIT_KEY = "upper_limit"
_X_AXIS_KEY = "x_axis"
_Y_AXIS_KEY = "y_axis"
# excel values
_TITLE_NAME = None
_LOWER_LIMIT_NAME = None
_UPPER_LIMIT_NAME = None
_X_AXIS_NAME = None
_Y_AXIS_NAME = None
# keys to access ColumnDataSources
_PLOT_SOURCE = "plot_source"
_TABLE_SOURCE = "table_source"
_Y_MAX = "y_axis_max"
_Y_MIN = "y_axis_min"
_X_MAX = "x_axis_max"
_X_MIN = "x_axis_min"
# script arguments for testing/development
_TEST_ARGV1 = r"C:\Users\Alfred\Documents\GitHub\Python\Custom Libraries\test_data.xlsx"
_TEST_ARGV2 = r"C:\Users\Alfred\Documents\GitHub\Python\Custom Libraries\test_output.json"

#~~~~  PUBLIC GLOBAL VARIABLES  ~~~~#

#~~~~  PRIVATE CLASSES  ~~~~#

#~~~~  PUBLIC CLASSES  ~~~~#

#~~~~  PRIVATE FUNCTIONS  ~~~~#
def _is_string_number(string: str) -> bool:
    """Check if string contents represent a number.
    
    Args:
        string: what to check (str)
    Returns:
        result of check (bool)
    """
    
    # terminate early
    if string == "":
        return False
    
    try:
        float(string)
    except ValueError:
        return False
    else:
        return True
    
def _calculate_average(data_set: pd.Series) -> float:
    """Calculate the average of a given data set.
    
    Args:
        data_set: data to use for average (Series)
    Returns:
        average (float)
    """
    
    average = data_set.mean(axis=0)
    rounded_average = round(average, _PRECISION)

    return rounded_average
    
def _calculate_average_moving_range(data_set: pd.Series, subset_length: int) -> float:
    """Calculate the average mR of a given data set.
    
    Args:
        data_set: data to use for mR (Series)
        subset_length: length of data subsets to use (int)
    Returns:
        average mR (float)
    """
    
    count = 0.0
    # data subsets to calculate mR on
    element_pairs = zip(data_set[:-(subset_length - 1)], data_set[(subset_length - 1):])
    # calculations
    for (left, right) in element_pairs:
        count += abs(left - right)
        
    result = count / (len(data_set) - (subset_length - 1))
    rounded_result = round(result, _PRECISION)
    
    return rounded_result
    
def _calculate_variation_limits(data_set):
    """Calculate the upper/lower range limits of a data set.
    
    Args:
        data_set: data to use for URL/LRL (Series)
    Returns:
        (upper, lower) (float 2-tuple)
    """
    
    # calculate averages
    average = _calculate_average(data_set)
    average_moving_range = _calculate_average_moving_range(data_set, 2)
    
    # calculate limits
    upper_natural_process_limits = average + (2.66 * average_moving_range)
    lower_natural_process_limits = average - (2.66 * average_moving_range)
    
    result = (lower_natural_process_limits, upper_natural_process_limits)
    rounded_result = (round(result[0], _PRECISION), round(result[1], _PRECISION))
    
    return rounded_result

def _calculate_cpk(data_set, lower, upper):
    """Calculate the cpk of a given data set.
    
    Args:
        data_set: data to use (Series)
        lower: lower limit (float)
        upper: upper limit (float)
    Returns:
        cpk (float)
    """

    arr = np.array([x for x in data_set]).ravel()
    sigma = np.std(arr)
    mean = np.mean(data_set)
    
    left = np.float64(upper - mean) / (3 * sigma)
    right = np.float64(mean - lower) / (3 * sigma)
    
    result = min(left, right)
    rounded_result = round(result, _PRECISION)
    
    return rounded_result

def _calculate_outside_limits(data_set, lower, upper):
    """Calculate the amount of values outside the limits.
    
    Args:
        data_set: data to use (Series)
        lower: lower limit (float)
        upper: upper limit (float)        
    Returns:
        (number, percent) (float 2-tuple)
    """
    
    length = data_set.shape[0]
    count = 0.0
    for x in data_set:
        if x < lower or x > upper:
            count += 1
            
    result = (count, round(count * 100 / length))
    rounded_result = (result[0], round(result[1], _PRECISION))
    
    return rounded_result

def _update_globals(constants_df):
    """Update global variables.
    
    Args:
        constants_df: Constants DataFrame to parse (DataFrame)
    Returns:
        None
    """
    
    # globals
    global _TITLE_NAME
    global _X_AXIS_NAME
    global _Y_AXIS_NAME
    global _UPPER_LIMIT_NAME
    global _LOWER_LIMIT_NAME
    
    # update globals
    _TITLE_NAME = constants_df.at[_TITLE_KEY, 1]
    _X_AXIS_NAME = constants_df.at[_X_AXIS_KEY, 1]
    _Y_AXIS_NAME = constants_df.at[_Y_AXIS_KEY, 1]
    _UPPER_LIMIT_NAME = constants_df.at[_UPPER_LIMIT_KEY, 1]
    _LOWER_LIMIT_NAME = constants_df.at[_LOWER_LIMIT_KEY, 1]
        
def _make_constant_data(data_df, constants_df):
    """Determine constant data from excel data.
    
    Args:
        data_df: Data DataFrame to parse (DataFrame)
        constants_df: Constants DataFrame to parse (DataFrame)
    Returns:
        {_PLOT_SOURCE: ColumnDataSource, 
         _X_MAX: int,
         _X_MIN: int,
         _Y_MAX: float,
         _Y_MIN: float} (dict)
    """
    
    # get raw data
    constant_data = {}
    constant_data[_PLOT_SOURCE] = bkms.ColumnDataSource(data=data_df) 

    # get derived data
    constant_data[_Y_MAX] = data_df.loc[:, _Y_AXIS_NAME].max()
    constant_data[_Y_MIN] = data_df.loc[:, _Y_AXIS_NAME].min()
    constant_data[_X_MAX] = len(data_df.loc[:, _X_AXIS_NAME]) - 1
    constant_data[_X_MIN] = 0

    # append useful info
    # hover_index = pd.DatetimeIndex(data = pd.to_datetime(constant_data["x_axis"]))
    # input_dict["dates"] = hover_index.format()
    
    return constant_data    

def _make_variable_data(data_df, constants_df, constant_data):
    """Determine variable data from constant_data and excel data.
    
    Args:
        data_df: Data DataFrame to parse (DataFrame)
        constants_df: Constants DataFrame to parse (DataFrame)
        constant_data: constant data (dict)
    Returns:
            {_PLOT_SOURCE: ColumnDataSource, 
             _TABLE_SOURCE: ColumnDataSource,
             _X_MAX: int,
             _X_MIN: int,
             _Y_MAX: float,
             _Y_MIN: float} (dict)        
    """
    
    # relevant data
    y_axis = data_df.loc[:, _Y_AXIS_NAME]
    x_axis = data_df.loc[:, _X_AXIS_NAME]

    # source init
    variable_data = {}
    table_dict = {"index": ["average",
                            "cpk",
                            "lower variation limit",
                            "upper variation limit",
                            "outside pass-fail (num)",
                            "outside pass-fail (%)"],
                  "value": [_calculate_average(y_axis), 
                            _calculate_cpk(y_axis, _LOWER_LIMIT_NAME, _UPPER_LIMIT_NAME), 
                            _calculate_variation_limits(y_axis)[0],
                            _calculate_variation_limits(y_axis)[1],
                            _calculate_outside_limits(y_axis, _LOWER_LIMIT_NAME, _UPPER_LIMIT_NAME)[0],
                            _calculate_outside_limits(y_axis, _LOWER_LIMIT_NAME, _UPPER_LIMIT_NAME)[1]]}
                             
    variable_data[_PLOT_SOURCE] = bkms.ColumnDataSource(data=data_df)
    variable_data[_TABLE_SOURCE] = bkms.ColumnDataSource(data=table_dict)
    variable_data[_Y_MAX] = max(y_axis)
    variable_data[_Y_MIN] = min(y_axis)
    variable_data[_X_MAX] = len(x_axis) - 1
    variable_data[_X_MIN] = 0

    return variable_data  

def _variation_pre_analysis(file_path: str):
    """Parse and prepare data for analysis.
    
    Args:
        file_path: excel file path (str)
    Returns:
        plot/widget sources (ColumnDataSource 2-tuple)
    """
    
    # grab data
    data_df = pd.read_excel(io=file_path, sheetname=_DATA_SHEET_NAME)
    constants_df = pd.read_excel(io=file_path, sheetname=_CONSTANTS_SHEET_NAME, header=None, index_col=0)
    
    # update globals
    _update_globals(constants_df)
    
    # clean variable data
    data_df = data_df.round(decimals={_Y_AXIS_NAME: _PRECISION})
    data_df = data_df.drop_duplicates()
    data_df = data_df.sort_values(by=[_X_AXIS_NAME, _Y_AXIS_NAME])
    
    # stucture data
    constant_data = _make_constant_data(data_df=data_df, constants_df=constants_df)
    variable_data = _make_variable_data(data_df=data_df, constants_df=constants_df, constant_data=constant_data)
    
    return (constant_data, variable_data)
    
def _create_variation_UI(constant_data, variable_data):
    """Given a data set, create the corresponding UI components.
    
    Args:
        constant_data: constant data (dict)
        variable_data: variable data (dict)
    Returns:
        None
    """

    # commonly used
    constant_source = constant_data[_PLOT_SOURCE]
    constant_source_data = constant_source.data
    constants_df = constant_source.to_df()
    variable_source = variable_data[_PLOT_SOURCE]
    variable_table_source = variable_data[_TABLE_SOURCE]
    
    # init figure
    figure = bkp.figure(title=_TITLE_NAME,
                        x_axis_label=_X_AXIS_NAME, 
                        y_axis_label=_Y_AXIS_NAME, 
                        x_axis_type="datetime",
                        y_axis_type="linear",
                        plot_width=1200)
    # figure.add_tools(bkm.HoverTool(tooltips=[("x", "@{}".format(constant_data[_X_AXIS_KEY])), ("y", "@{}".format(constant_data[_Y_AXIS_KEY])), ("index", "$index")]))  
    figure.circle(x=_X_AXIS_NAME, y=_Y_AXIS_NAME, 
                  size = 5, fill_color = "white", source=variable_source, legend="points")
    figure.line(x=_X_AXIS_NAME, y=_Y_AXIS_NAME, source=variable_source, legend="lines")
    # configure and add lines
    average = bkm.Span(dimension="width", line_color="#000000", line_dash="dashed",
                       location=variable_table_source.data["value"][0], line_width=3)
    pf_upper = bkm.Span(dimension="width", line_color="#FF0000", line_dash="dashed",
                        location=_UPPER_LIMIT_NAME, line_width=3)
    pf_lower = bkm.Span(dimension="width", line_color="#FF0000", line_dash="dashed",
                        location=_LOWER_LIMIT_NAME, line_width=3)
    variation_upper = bkm.Span(dimension="width", line_color="#FFA500", line_dash="dashed",
                               location=variable_table_source.data["value"][3], line_width=3)
    variation_lower = bkm.Span(dimension="width", line_color="#FFA500", line_dash="dashed",
                               location=variable_table_source.data["value"][2], line_width=3)
    figure.add_layout(average)
    figure.add_layout(pf_upper)
    figure.add_layout(pf_lower)
    figure.add_layout(variation_upper)
    figure.add_layout(variation_lower)
    
    # widget callbacks & misc nested functions
    def update_plot(changed_aspect, new_value):
        print("update_plot")
        upper_limit = variable_data[_Y_MAX]
        lower_limit = variable_data[_Y_MIN]
        upper_index = variable_data[_X_MAX]
        lower_index = variable_data[_X_MIN]
        
        if changed_aspect == "upper_limit":
            upper_limit = min(np.float64(new_value), constant_data[_Y_MAX])
            variable_data[_Y_MAX] = upper_limit
        elif changed_aspect == "lower_limit":
            lower_limit = max(np.float64(new_value), constant_data[_Y_MIN])  
            variable_data[_Y_MIN] = lower_limit
        elif changed_aspect == "upper_index":
            upper_index = min(int(new_value), constant_data[_X_MAX])
            variable_data[_X_MAX] = upper_index
        elif changed_aspect == "lower_index":
            lower_index = max(int(new_value), constant_data[_X_MIN])
            variable_data[_X_MIN] = lower_index
        
        print("upper_limit: {}".format(upper_limit))
        print("lower_limit: {}".format(lower_limit))
        print("upper_index: {}".format(upper_index))
        print("lower_index: {}".format(lower_index))
        
        new_plot_data = constants_df.iloc[lower_index: upper_index + 1, :]
        new_plot_data = new_plot_data[(new_plot_data[_Y_AXIS_NAME] <= upper_limit) & 
                                      (new_plot_data[_Y_AXIS_NAME] >= lower_limit)]  
        new_plot_dict = {_X_AXIS_NAME: new_plot_data[_X_AXIS_NAME].as_matrix(), _Y_AXIS_NAME: new_plot_data[_Y_AXIS_NAME].as_matrix()}
        variable_data[_PLOT_SOURCE].data = new_plot_dict
        print("update_plot")
        
    def update_data():
        print("update_data")
        # commonly used
        y_axis = variable_source.data[_Y_AXIS_NAME]
        
        # make updates
        table_dict = {"index": ["average",
                                "cpk",
                                "lower variation limit",
                                "upper variation limit",
                                "outside pass-fail (num)",
                                "outside pass-fail (%)"],
                    "value": [_calculate_average(y_axis), 
                                _calculate_cpk(y_axis, _LOWER_LIMIT_NAME, _UPPER_LIMIT_NAME), 
                                _calculate_variation_limits(y_axis)[0],
                                _calculate_variation_limits(y_axis)[1],
                                _calculate_outside_limits(y_axis, _LOWER_LIMIT_NAME, _UPPER_LIMIT_NAME)[0],
                                _calculate_outside_limits(y_axis, _LOWER_LIMIT_NAME, _UPPER_LIMIT_NAME)[1]]}
                                
        variable_data[_TABLE_SOURCE].data = table_dict   
        print("update_data")
            
    def update_plot_lines():
        print("update_plot_lines")
        average.location = variable_table_source.data["value"][0]
        variation_upper.location = variable_table_source.data["value"][3]
        variation_lower.location = variable_table_source.data["value"][2]   
        print("update_plot_lines")     
    
    def callback_plot_upper_limit(attr, old, new):
        print("callback_plot_upper_limit")
        # terminate early
        if _is_string_number(new) is False:
            y_upper_input.value = old
            return
        formatted_new = np.float("{:.3f}".format(np.float64(new)))
        if formatted_new == old:
            y_upper_input.value = old
            return
        if formatted_new < variable_data[_Y_MIN]:
            y_upper_input.value = old
            return
        
        # update source (variable_data) and max y value
        update_plot("upper_limit", new)
        
        # update variable_data table info
        update_data()

        # update plot lines
        update_plot_lines()
        
        # change input visual if exceeding max/min
        y_upper_input.value = str(variable_data[_Y_MAX])
        print("callback_plot_upper_limit")
        
    def callback_plot_lower_limit(attr, old, new):
        print("callback_plot_lower_limit")
        # terminate early
        if _is_string_number(new) is False or old == new or np.float("{:.3f}".format(np.float64(new))) > variable_data[_Y_MAX]:
            y_lower_input.value = old
            return
            
        # update variable_data source and min y value
        update_plot("lower_limit", new)
                
        # update variable_data table info
        update_data()
        
        # update input source
        update_plot_lines()
                
        # change input visual if exceeding max/min
        y_lower_input.value = str(variable_data[_Y_MIN])
        print("callback_plot_lower_limit")

    def callback_plot_upper_index(attr, old, new):
        print("callback_plot_upper_index")
        # terminate early
        if _is_string_number(new) is False or old == new or int(new) < variable_data[_X_MIN]:
            x_upper_input.value = old
            return
            
        # update variable_data source and max x index
        update_plot("upper_index", new)
        
        # update variable_data table info
        update_data()
        
        # update plot lines
        update_plot_lines()
        
        # change input visual if exceeding max/min
        x_upper_input.value = str(variable_data[_X_MAX])
        print("callback_plot_upper_index")
        
    def callback_plot_lower_index(attr, old, new):
        print("callback_plot_lower_limit")
        # terminate early
        if _is_string_number(new) is False or old == new or int(new) > variable_data[_X_MAX]:
            x_lower_input.value = old
            return
        
        # update variable_data source and min x index
        update_plot("lower_index", new)
        
        # update variable_data table info
        update_data()
        
        # update plot lines
        update_plot_lines()
        
        # change input visual if exceeding max/min
        x_lower_input.value = str(variable_data[_X_MIN])
        print("callback_plot_lower_limit")
        
    # def callback_save_output():
    #     tools.create_timestamp(output_file_path)
    #     with open(output_file_path, "a") as f:
    #         dict = {"input": [(item, value[0]) for item, value in input_source.data.items() if len(value) == 1],
    #                 "output": [(item, value) for item, value in zip(output_data.data["calculation"], output_data.data["value"])]}
    #         JSON_STRING = json.dumps(dict, indent = 2, sort_keys = True)
    #         f.write(JSON_STRING + "\n\n")
            
    # configure input widgets
    y_upper_input = bkm.TextInput(title="Y Max Value (inclusive)", 
                                  value=str(constant_data[_Y_MAX]))
    y_upper_input.on_change("value", callback_plot_upper_limit)
    y_lower_input = bkm.TextInput(title="Y Min Value (inclusive)", 
                                  value=str(constant_data[_Y_MIN]))
    y_lower_input.on_change("value", callback_plot_lower_limit)
    x_upper_input = bkm.TextInput(title="X Max Index (inclusive)", 
                                  value=str(constant_data[_X_MAX]))
    x_upper_input.on_change("value", callback_plot_upper_index)
    x_lower_input = bkm.TextInput(title="X Min Index (inclusive)", 
                                  value=str(constant_data[_X_MIN]))
    x_lower_input.on_change("value", callback_plot_lower_index)
    save_data = bkm.Button(label="save data", button_type="success")
    # save_data.on_click(callback_save_output)
    
    # # configure output widgets
    table_column1 = bkmw.TableColumn(field="index", title="Calculation", sortable=False)
    table_column2 = bkmw.TableColumn(field="value", title="Value", sortable=False)
    table_output = bkmw.DataTable(source=variable_data[_TABLE_SOURCE], columns=[table_column1, table_column2], 
                                  row_headers=False, sizing_mode="scale_width", fit_columns=False)    

    # configure and add figure legend
    # figure.legend.location = "top_left"
    figure.legend.click_policy="hide"
    figure.legend.border_line_width = 3
    figure.legend.border_line_color = "navy" 
    figure.legend.background_fill_alpha = 0

    # # configure UI layout 
    input_left = bkl.column([y_upper_input, y_lower_input])
    input_right = bkl.column([x_upper_input, x_lower_input])
    text_input = bkl.row([input_left, input_right])
    input = bkl.column([text_input, save_data])
    widgets = bkl.row([input, table_output])
    plot_and_io = bkl.column([figure, widgets])
    #@debug
    bkio.curdoc().add_root(plot_and_io)

    return None   

#~~~~  PUBLIC FUNCTIONS  ~~~~#
def variation_analysis(file_path: str) -> None:
    """Perform and display a variation analysis.
    
    Args:
        file_path: excel file path (str)
    Returns:
        None
    """
    
    constant_data, variable_data = _variation_pre_analysis(file_path)
    _create_variation_UI(constant_data, variable_data)
    
    return None

#~~~~  MAIN  ~~~~#
variation_analysis(_TEST_ARGV1)

#~~~~  DEAD CODE  ~~~~#

# def _filter_out_nonnumbers(data_set):
#     """Filter out non-number data set elements.
#     
#     Args:
#         data_set: what to filter (list)
#     Returns:
#         filtered copy of argument (list)
#     """
#     
#     print("debug: _filter_out_nonnumbers")
#     return [x for x in data_set if _is_string_number(x)]

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
#         # display_subset = create_UI(_variation_pre_analysis(sys.argv[1]), sys.argv[2])
#         display_subset = create_UI(_variation_pre_analysis(_TEST_ARGV1), _TEST_ARGV2)
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
#         # get multi-column data groups sequentially
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

# def _round_df(df):
#     """Round float values.
#     
#     Args:
#         df: DataFrame to round.
#     Returns:
#         rounded DataFrame (DataFrame)
#     """
#     
#     rounded_df = df.round({"voltage (V)": 3})
#     
#     return rounded_df
#     
# def _filter_duplicates(df):
#     """Filter duplicates in place.
#     
#     Args:
#         df: DataFrame to filter (DataFrame)
#     Returns:
#         number of duplicates found (int)
#     """
#     
#     num_rows_before = df.shape[0]
#     df.drop_duplicates(inplace=True)
#     num_rows_after = df.shape[0]
#     number_of_dupes = num_rows_before - num_rows_after
#     
#     return number_of_dupes
# 
# def _sort_df(df):
#     """Sort DataFrame in place.
#     
#     Args:
#         df: DataFrame to sort (DataFrame)
#     Returns:
#         None
#     """
#     
#     df.sort_values(by=["datetime", "voltage (V)"], inplace=True)
#     
#     return None