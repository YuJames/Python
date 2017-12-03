"""
NAME:
    spc

DESCRIPTION:
    Run this module as a script. This script creates an interactive web browser
    UI that displays inputted excel data and its analysis (with the option to 
    save analysis data), assuming the x-axis will be in datetime format. The 
    purpose is to encourage statistical process control (SPC) for the analyzed 
    subject. 
    
    This module uses Bokeh to create interactive web UIs. The purpose is to
    encourage statistical process control (SPC) for the analyzed data.

ARGUMENTS:
    argv[1]: excel file path
    argv[2]: excel parse settings; {sheet_name, x_axis, y_axis, title, pf_lower_limit, pf_upper_limit}
    argv[3]: saved data file path
"""

#~~~~  imports  ~~~~v
import ast
import copy
import json
import subprocess
import sys
import time

import bokeh.client as bkc
import bokeh.io as bkio
import bokeh.layouts as bkl
import bokeh.models as bkm
import bokeh.models.sources as bkms
import bokeh.models.widgets as bkmw
import bokeh.plotting as bkp
import numpy as np
import pandas as pd

import intern_developed_tools

#****  global variables  ****v

#****  classes  ****v

#****  support functions  ****v
def is_string_number(string):
    """Check if string contents represent a number.
    
    Arguments:
        string: what to check (string)
    Return:
        result of check (bool)
    """
    
    try:
        float(string)
        return True
    except ValueError:
        return False

def filter_out_nonnumbers(data_set):
    """Filter out non-number data set elements.
    
    Arguments:
        data_set: what to filter (list)
    Return:
        filtered copy of argument (list)
    """
    
    return [x for x in data_set if is_string_number(x)]
    
def calculate_average(data_set):
    """Calculate the average of a given data set.
    
    Arguments:
        data_set: data to use for average (float list)
    Return:
        average (float)
    """
    
    filtered = filter_out_nonnumbers(data_set)
    return sum(filtered)/len(filtered)
    
def calculate_average_moving_range(data_set, subset_length):
    """Calculate the average mR of a given data set.
    
    Arguments:
        data_set: data to use for mR (float list)
        subset_length: length of data subsets to use (int)
    Return:
        average mR (float)
    """
    
    result = 0.0
    
    filtered = filter_out_nonnumbers(data_set)
    # data subsets to calculate mR on
    element_pairs = zip(filtered[:-(subset_length - 1)], filtered[(subset_length - 1):])
    
    # calculations
    for (left, right) in element_pairs:
        result += abs(left - right)
    result /= (len(filtered) - (subset_length - 1))
    
    return result
    
def calculate_variation_limits(data_set):
    """Calculate the upper/lower range limits of a data set.
    
    Arguments:
        data_set: data to use for URL/LRL (float list)
    Return:
        (upper, lower) (float 2-tuple)
    """
    
    # calculate needed info
    filtered = filter_out_nonnumbers(data_set)
    average = calculate_average(filtered)
    average_moving_range = calculate_average_moving_range(filtered, 2)
    
    # calculate limits
    upper_natural_process_limits = average + (2.66 * average_moving_range)
    lower_natural_process_limits = average - (2.66 * average_moving_range)
    
    return (lower_natural_process_limits, upper_natural_process_limits)

def calculate_cpk(data_set, lower, upper):
    """Calculate the cpk of a given data set.
    
    Arguments:
        data_set: data to use (float list)
        lower: lower limit (float)
        upper: upper limit (float)
    Return:
        cpk (float)
    """
    
    filtered = filter_out_nonnumbers(data_set)
    arr = np.array([x for x in filtered]).ravel()
    sigma = np.std(arr)
    mean = np.mean(filtered, dtype = np.float64)
    
    left = float(upper - mean) / (3 * sigma)
    right = float(mean - lower) / (3 * sigma)
    return min(left, right)

def calculate_outside_limits(data_set, lower, upper):
    """Calculate the amount of values outside the limits.
    
    Arguments:
        data_set: data to use (float list)
        lower: lower limit (float)
        upper: upper limit (float)        
    Return:
        (number, percent) (float 2-tuple)
    """
    
    filtered = filter_out_nonnumbers(data_set)
    length = float(len(filtered))
    count = 0.0
    for x in data_set:
        if x < lower or x > upper:
            count += 1
    return (count, count * 100 / length)
    
#****  main functions  ****v
def calculate_input_source(input_source = None, **kwargs):
    """Initialize or update info for a source.
    
    Arguments:
        input_source: source to update (None or ColumnDataSource)
        kwargs: values used to initialize or update
    Return:
        source for input calculations (ColumnDataSource or None)
    """
    
    if input_source is None:
        start = kwargs["start"]
        end = kwargs["end"]
        excel_dataframe = kwargs["excel_dataframe"]
        parse_settings = kwargs["parse_settings"]
        
        input_dictionary = {}
        input_dictionary["x_axis"] = excel_dataframe.iloc[start:end - 1, parse_settings["x_axis"]].tolist()
        input_dictionary["y_axis"] = excel_dataframe.iloc[start:end - 1, parse_settings["y_axis"]].tolist()
        input_dictionary["x_axis_label"] = [excel_dataframe.iloc[start:end - 1, parse_settings["x_axis"]].name]
        input_dictionary["y_axis_label"] = [excel_dataframe.iloc[start:end - 1, parse_settings["y_axis"]].name]
        input_dictionary["title"] = [excel_dataframe.iat[start, parse_settings["title"]]]
        input_dictionary["pf_lower_limit"] = [excel_dataframe.iat[start, parse_settings["pf_lower_limit"]]]
        input_dictionary["pf_upper_limit"] = [excel_dataframe.iat[start, parse_settings["pf_upper_limit"]]]
        # append useful info
        hover_index = pd.DatetimeIndex(data = pd.to_datetime(input_dictionary["x_axis"]))
        input_dictionary["dates"] = hover_index.format()
        input_dictionary["x_axis_copy"] = copy.deepcopy(input_dictionary["x_axis"])
        input_dictionary["y_axis_copy"] = copy.deepcopy(input_dictionary["y_axis"])
        input_dictionary["lower_limit"] = [min(input_dictionary["y_axis"])]
        input_dictionary["upper_limit"] = [max(input_dictionary["y_axis"])]
        input_dictionary["lower_index"] = [0]
        input_dictionary["upper_index"] = [len(input_dictionary["y_axis"]) - 1]
        input_dictionary["mask"] = ["strings do not show up on plots"] 
        
        input_source = bkms.ColumnDataSource(input_dictionary)
        return input_source
        
    else:
        upper_limit = kwargs["upper_limit"]
        lower_limit = kwargs["lower_limit"]
        upper_index = kwargs["upper_index"]
        lower_index = kwargs["lower_index"]
        new_data = kwargs["new_data"]
        mask = kwargs["mask"]
        
        for i in range(len(new_data)):
            if i < lower_index or i > upper_index or new_data[i] < lower_limit or new_data[i] > upper_limit:
                new_data[i] = mask 
        input_source.data["y_axis"] = new_data
        
        input_source.data["upper_limit"] = [upper_limit]   
        input_source.data["lower_limit"] = [lower_limit]
        input_source.data["upper_index"] = [upper_index]
        input_source.data["lower_index"] = [lower_index]
            
def calculate_output_source(input_source, output_source = None):
    """Initialize or update info for a source.
    
    Arguments:
        input_source: source with base data for calculations (ColumnDataSource)
        output_source: source to update (None or ColumnDataSource)
    Return:
        source for output calculations (ColumnDataSource or None)
    """      
    
    # relevant data
    filtered = filter_out_nonnumbers(input_source.data["y_axis"])
    pf_lower_limit = input_source.data["pf_lower_limit"][0]
    pf_upper_limit = input_source.data["pf_upper_limit"][0]
    original_values = input_source.data["y_axis_copy"]
    
    # source init
    if output_source is None:
        output_dictionary = {}
        output_dictionary["calculation"] = ["average", "cpk", 
                                            "lower variation limit", "upper variation limit", 
                                            "outside pass-fail (num)", "outside pass-fail (%)"]
        output_dictionary["value"] = [calculate_average(filtered),
                                      calculate_cpk(filtered, 
                                                    pf_lower_limit, 
                                                    pf_upper_limit),
                                      calculate_variation_limits(filtered)[0],
                                      calculate_variation_limits(filtered)[1],
                                      calculate_outside_limits(filtered,
                                                               pf_lower_limit,
                                                               pf_upper_limit)[0],
                                      calculate_outside_limits(filtered,
                                                               pf_lower_limit,
                                                               pf_upper_limit)[1]]
                                      
        output_source = bkms.ColumnDataSource(output_dictionary)
        return output_source
    # source update
    else:
        output_source.data["value"] = [calculate_average(filtered),
                                       calculate_cpk(filtered, 
                                                     pf_lower_limit, 
                                                     pf_upper_limit),
                                       calculate_variation_limits(filtered)[0],
                                       calculate_variation_limits(filtered)[1],
                                       calculate_outside_limits(filtered,
                                                                pf_lower_limit,
                                                                pf_upper_limit)[0],
                                       calculate_outside_limits(filtered,
                                                                pf_lower_limit,
                                                                pf_upper_limit)[1]]
def get_data_subsets(file_path, parse_settings):
    """From an excel sheet, find data subsets separated by title values.
    
    Arguments:
        file_path: excel file path (string)
        parse_settings: {sheet_name, x_axis, y_axis, x_axis_label, y_axis_label, 
                         title, pf_lower_limit, pf_upper_limit} (dictionary)
    Return:
        plot/widget sources (ColumnDataSource 2-tuple generator)
    """

    # grab all excel data
    parse_settings = ast.literal_eval(parse_settings)
    excel_dataframe = pd.read_excel(file_path, sheetname = parse_settings["sheet_name"])
    
    # separate by test type
    start_indices = []
    end_indices = []
    current_title = ""
    for i, title in enumerate(excel_dataframe.iloc[:, parse_settings["title"]]):
        if i == 0:
            current_title = title
            start_indices.append(i)
        elif title is not current_title:
            current_title = title
            end_indices.append(i)
            start_indices.append(i)
    else:
        if len(start_indices) != len(end_indices):
            end_indices.append(i)

    for start, end in zip(start_indices, end_indices):
        input_source = calculate_input_source(start = start, end = end, 
                                              excel_dataframe = excel_dataframe,
                                              parse_settings = parse_settings)
        output_source = calculate_output_source(input_source)
        
        yield (input_source, output_source)
                                                                                
def create_UI(sources, output_file_path):
    """Given a data set, create the corresponding UI components.
    
    Arguments:
        sources: grouped data & calculations (ColumnDataSource 2-tuple)
        output_file_path: json file (string)
    Return:
        UI components (Layout)
    """
    
    # initial sources, and figure configurations
    input_source = sources[0]
    output_source = sources[1]
    figure = bkp.figure(title = input_source.data["title"][0], 
                        x_axis_label = input_source.data["x_axis_label"][0], 
                        y_axis_label = input_source.data["y_axis_label"][0], 
                        x_axis_type = "datetime",
                        plot_width = 1200)
    figure.add_tools(bkm.HoverTool(tooltips=[("x", "@dates"), ("y", "@y_axis"), ("index", "$index")]))  
    figure.circle(x = "x_axis", y = "y_axis", size = 5, fill_color = "white", 
                  source = input_source)
                  
    # lines configuration
    average = bkm.Span(dimension = "width", line_color = "#000000", line_dash = "dashed",
                       location = output_source.data["value"][0])
    pf_upper = bkm.Span(dimension = "width", line_color = "#FF0000", line_dash = "dashed",
                        location = input_source.data["pf_upper_limit"][0])
    pf_lower = bkm.Span(dimension = "width", line_color = "#FF0000", line_dash = "dashed",
                        location = input_source.data["pf_lower_limit"][0])
    variation_upper = bkm.Span(dimension = "width", line_color = "#FFA500", line_dash = "dashed",
                               location = output_source.data["value"][3])
    variation_lower = bkm.Span(dimension = "width", line_color = "#FFA500", line_dash = "dashed",
                               location = output_source.data["value"][2])
    figure.add_layout(average)
    figure.add_layout(pf_upper)
    figure.add_layout(pf_lower)
    figure.add_layout(variation_upper)
    figure.add_layout(variation_lower)
    
    # widget callbacks & misc nested functions
    def update_plot_lines():
        average.location = output_source.data["value"][0]
        variation_upper.location = output_source.data["value"][3]
        variation_lower.location = output_source.data["value"][2]        
    
    def callback_plot_upper_limit(attr, old, new):
        # early termination
        if is_string_number(new) is False or float(old) == float(new):
            return
        elif float(new) < input_source.data["lower_limit"][0]:
            return
        
        # relevant data
        lower_index = input_source.data["lower_index"][0]
        upper_index = input_source.data["upper_index"][0]
        lower_limit = input_source.data["lower_limit"][0]
        upper_limit = min(float(new), max(input_source.data["y_axis_copy"]))
        new_data = copy.deepcopy(input_source.data["y_axis_copy"])
        mask = input_source.data["mask"][0]
        
        # update input source
        calculate_input_source(input_source, 
                               lower_index = lower_index, upper_index = upper_index, 
                               lower_limit = lower_limit, upper_limit = upper_limit, 
                               new_data = new_data, mask = mask)
        
        # update output source
        calculate_output_source(input_source, output_source)
        
        # update plot lines
        update_plot_lines()
        
        # change input visual if exceeding max/min
        y_upper_input.value = str(upper_limit)
        
        # callbacks can have a series of actions to take after an interaction w/the inputs has taken place.
        # this can include checking values, as pavan was interested in.
        # e.g. check output_source value "cpk" and maybe sending an email or change a plot element's color
    def callback_plot_lower_limit(attr, old, new):
        # early termination
        if is_string_number(new) is False or float(old) == float(new):
            return
        elif float(new) > input_source.data["upper_limit"][0]:
            return
            
        # relevant data
        lower_index = input_source.data["lower_index"][0]
        upper_index = input_source.data["upper_index"][0]
        lower_limit = max(float(new), min(input_source.data["y_axis_copy"]))
        upper_limit = input_source.data["upper_limit"][0]
        new_data = copy.deepcopy(input_source.data["y_axis_copy"])
        mask = input_source.data["mask"][0]
        
        # update input source
        calculate_input_source(input_source, 
                               lower_index = lower_index, upper_index = upper_index, 
                               lower_limit = lower_limit, upper_limit = upper_limit, 
                               new_data = new_data, mask = mask)
    
        # update output source
        calculate_output_source(input_source, output_source)
        
        # update plot lines
        update_plot_lines()
                
        # change input visual if exceeding max/min
        y_lower_input.value = str(lower_limit)
        
    def callback_plot_upper_index(attr, old, new):
        # early termination
        if is_string_number(new) is False or int(old) == int(new):
            return
        elif int(new) < input_source.data["lower_index"][0]:
            return
            
        # relevant data
        lower_index = input_source.data["lower_index"][0]
        upper_index = min(int(new), len(input_source.data["y_axis_copy"]) - 1)
        lower_limit = input_source.data["lower_limit"][0]
        upper_limit = input_source.data["upper_limit"][0]
        new_data = copy.deepcopy(input_source.data["y_axis_copy"])
        mask = input_source.data["mask"][0]
        
        # update input source
        calculate_input_source(input_source, 
                               lower_index = lower_index, upper_index = upper_index, 
                               lower_limit = lower_limit, upper_limit = upper_limit, 
                               new_data = new_data, mask = mask)
        
        # update output source
        calculate_output_source(input_source, output_source)
        
        # update plot lines
        update_plot_lines()
        
        # change input visual if exceeding max/min
        x_upper_input.value = str(upper_index)
        
    def callback_plot_lower_index(attr, old, new):
        # early termination
        if is_string_number(new) is False or int(old) == int(new):
            return
        elif int(new) > input_source.data["upper_index"][0]:
            return
        
        # relevant data
        lower_index = max(int(new), 0)
        upper_index = input_source.data["upper_index"][0]
        lower_limit = input_source.data["lower_limit"][0]
        upper_limit = input_source.data["upper_limit"][0]
        new_data = copy.deepcopy(input_source.data["y_axis_copy"])
        mask = input_source.data["mask"][0]
    
        # update input source
        calculate_input_source(input_source, 
                               lower_index = lower_index, upper_index = upper_index, 
                               lower_limit = lower_limit, upper_limit = upper_limit, 
                               new_data = new_data, mask = mask)
        
        # update output source
        calculate_output_source(input_source, output_source)
        
        # update plot lines
        update_plot_lines()
        
        # change input visual if exceeding max/min
        x_lower_input.value = str(lower_index)
    
    def callback_save_output():
        intern_developed_tools.create_timestamp(output_file_path)
        with open(output_file_path, "a") as f:
            dict = {"input": [(item, value[0]) for item, value in input_source.data.items() if len(value) == 1],
                    "output": [(item, value) for item, value in zip(output_source.data["calculation"], output_source.data["value"])]}
            JSON_STRING = json.dumps(dict, indent = 2, sort_keys = True)
            f.write(JSON_STRING + "\n\n")
            
    # input widgets   
    y_upper_input = bkm.TextInput(title = "Upper Y Limit", value = "{}".format(input_source.data["upper_limit"][0]))
    y_upper_input.on_change("value", callback_plot_upper_limit)
    y_lower_input = bkm.TextInput(title = "Lower Y Limit", value = "{}".format(input_source.data["lower_limit"][0]))
    y_lower_input.on_change("value", callback_plot_lower_limit)
    x_upper_input = bkm.TextInput(title = "Upper X Index", value = "{}".format(input_source.data["upper_index"][0]))
    x_upper_input.on_change("value", callback_plot_upper_index)
    x_lower_input = bkm.TextInput(title = "Lower X Index", value = "{}".format(input_source.data["lower_index"][0]))
    x_lower_input.on_change("value", callback_plot_lower_index)
    save_data = bkm.Button(label = "save data", button_type="success")
    save_data.on_click(callback_save_output)
    
    # output widgets
    table_column1 = bkmw.TableColumn(field = "calculation", title = "Calculation", sortable = False)
    table_column2 = bkmw.TableColumn(field = "value", title = "Value", sortable = False)
    table_output = bkmw.DataTable(source = output_source, columns = [table_column1, table_column2], 
                                  row_headers = False, sizing_mode = "scale_width", fit_columns = False)    

    # figure legend configurations
    figure.legend.border_line_width = 3
    figure.legend.border_line_color = "navy" 
    figure.legend.background_fill_alpha = 0

    # UI layout configurations
    input_left = bkl.column([y_upper_input, y_lower_input])
    input_right = bkl.column([x_upper_input, x_lower_input])
    text_input = bkl.row([input_left, input_right])
    input = bkl.column([text_input, save_data])
    widgets = bkl.row([input, table_output])
    plot_and_io = bkl.column([figure, widgets])
     
    return plot_and_io

#****  main  ****v
# DISPLAY ALL SCRIPT ARGUMENTS
print intern_developed_tools.make_formatted_title("script arguments")
intern_developed_tools.display_arguments()

# PARSE EXCEL, ANALYZE DATA, AND MAKE UI
print intern_developed_tools.make_formatted_title("parse/process all data subsets")
# init bokeh & track UI components
subprocess.Popen(["bokeh.exe", "serve"], shell = True)
time.sleep(5)
session = bkc.push_session(bkp.curdoc()) 
display_column_of_rows = []
# get multi-column data groups sequentially
for sources in get_data_subsets(sys.argv[1], sys.argv[2]):
    # create UI subset
    display_subset = create_UI(sources, sys.argv[3])
    
    # add to final UI superset
    display_column_of_rows.append(display_subset)
    
# DISPLAY ONTO WEB BROWSER
bkp.curdoc().add_root(bkl.column(display_column_of_rows))
session.show()
session.loop_until_closed()