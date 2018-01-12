#!/usr/bin/env python3

"""Bokeh data visualization.

This module uses Bokeh v.0.12.12 to create interactive web UIs for analyzing 
data. The purpose is to encourage statistical process control (SPC).

Arguments:
    argv[1]: excel file path
    argv[2]: config json file path
    argv[3]: saved data file path (currently not used)
    
ToDo:
    update docstrings
    rename functions
    make figure class
        improve callback_text_input
    change text input value to match closest value (not just if only exceeding max)?
        e.g. with y values of [1, 3, 6], a "max y" input of 5 would change to 3
    add more checks/preprocessing?
    fix "float division by zero error" (when sigma = 0)
        impossible? Give warning instead?
    Look into static type checking
        Do not run yet, but prepare code.
        float vs np.float64
        work on class methods?
    *improve docstrings
    *improve modularity (globals, fxns, variables)
    *improve naming
    *correct return vs return None vs nothing
    
*check consistently throughout project
"""

#~~~~  IMPORTS  ~~~~#
import enum
import json  # not currently used (will be)
import subprocess # not currently used
import sys
import time  # not currently used
import typing

from functools import partial

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
import tools

#~~~~  PRIVATE (GLOBAL CONSTANTS and ENUMS)  ~~~~#
class _TableCdsKey(enum.Enum):
    AVG = "average"
    CPK = "cpk"
    VAR_MAX = "variation_max"
    VAR_MIN = "variation_min"
    FAILS_NUM = "fails (num)"
    FAILS_RATIO = "fails (%)"

class _DataKey(enum.Enum):
    # keys to access _ConstantData and _VariableData
    EXCEL_DF = "excel_dataframe"
    PLOT_CDS = "plot_source"
    TABLE_CDS = "table_source"
    EXCEL_Y_MAX = "excel_y_max"
    EXCEL_Y_MIN = "excel_y_min"
    EXCEL_X_MAX = "excel_x_max"
    EXCEL_X_MIN = "excel_x_min"
    PLOT_Y_MAX = "plot_y_max"
    PLOT_Y_MIN = "plot_y_min"
    PLOT_X_MAX = "plot_x_max"
    PLOT_X_MIN = "plot_x_min"

_JsonKey = None        # stuff from json (title name, axis names, sheet names, etc)

class _WidgetKey(enum.Enum):
    Y_MAX_INPUT = "Y Max Value (inclusive)"
    Y_MIN_INPUT = "Y Min Value (inclusive)"
    X_MAX_INPUT = "X Max Index (inclusive)"
    X_MIN_INPUT = "X Min Index (inclusive)"
    COL_NAME_OUTPUT = "Calculation"
    COL_VALUE_OUTPUT = "Value"
    
# script arguments for testing/development
_TEST_ARGV1 = r"C:\Users\Alfred\Documents\GitHub\Python\Custom Libraries\test_data.xlsx"
_TEST_ARGV2 = r"C:\Users\Alfred\Documents\GitHub\Python\Custom Libraries\test_config.json"

#~~~~  PUBLIC (GLOBAL CONSTANTS and ENUMS)  ~~~~#

#~~~~  PRIVATE GLOBAL VARIABLES  ~~~~#

#~~~~  PUBLIC GLOBAL VARIABLES  ~~~~#

#~~~~  PRIVATE CLASSES  ~~~~#
class _VariationAnalysisData(object):
    col1 = "index"
    col2 = "value"    
    
    def __init__(self, data_df):
        # list commons
        y_axis = data_df.loc[:, _JsonKey.Y_NAME.value]
        x_axis = data_df.loc[:, _JsonKey.X_NAME.value]
        
        # make calcs
        table_dict = {self.__class__.col1: [_TableCdsKey.AVG.value,
                                            _TableCdsKey.CPK.value,
                                            _TableCdsKey.VAR_MAX.value,
                                            _TableCdsKey.VAR_MIN.value,
                                            _TableCdsKey.FAILS_NUM.value,
                                            _TableCdsKey.FAILS_RATIO.value],
                      self.__class__.col2: [_calc_average(y_axis), 
                                            _calc_cpk(y_axis, _JsonKey.LOWER_LIMIT.value, _JsonKey.UPPER_LIMIT.value), 
                                            _calc_variation_limits(y_axis)[1],
                                            _calc_variation_limits(y_axis)[0],
                                            _calc_failures(y_axis, _JsonKey.LOWER_LIMIT.value, _JsonKey.UPPER_LIMIT.value)[0],
                                            _calc_failures(y_axis, _JsonKey.LOWER_LIMIT.value, _JsonKey.UPPER_LIMIT.value)[1]]}
                                            
        # init members
        self.sources = {}
        self.data = {}
        # init sources
        self.sources[_DataKey.PLOT_CDS] = bkms.ColumnDataSource(data=data_df)
        self.sources[_DataKey.TABLE_CDS] = bkms.ColumnDataSource(data=table_dict)
        # init derived limits
        self.data[_DataKey.EXCEL_DF] = data_df 
        self.data[_DataKey.EXCEL_Y_MAX] = y_axis.max()
        self.data[_DataKey.EXCEL_Y_MIN] = y_axis.min()
        self.data[_DataKey.EXCEL_X_MAX] = x_axis.size - 1
        self.data[_DataKey.EXCEL_X_MIN] = 0 
        self.data[_DataKey.PLOT_Y_MAX] = y_axis.max()
        self.data[_DataKey.PLOT_Y_MIN] = y_axis.min()
        self.data[_DataKey.PLOT_X_MAX] = x_axis.size - 1
        self.data[_DataKey.PLOT_X_MIN] = 0 

    def get(self, key):
        """Get the value mapped to by a key.
        
        Args:
            key: key (_DataKey or _TableCdsKey)
        Returns:
            pd.DataFrame, bkms.ColumnDataSource, float, or int.
        """
        
        if key in _TableCdsKey:
            index_of_key = self.sources[_DataKey.TABLE_CDS].data[self.__class__.col1].index(key.value)
            return self.sources[_DataKey.TABLE_CDS].data[self.__class__.col2][index_of_key]
        elif key is _DataKey.PLOT_CDS or key is _DataKey.TABLE_CDS:
            return self.sources[key]
        else:
            return self.data[key]
               
    def set(self, key, value):
        """Set the value mapped to by a key.
        
        Args:
            key: key (_DataKey or _TableCdsKey)
        Returns:
            None
        """
        
        if key in _TableCdsKey:
            index_of_key = self.sources[_DataKey.TABLE_CDS].data[self.__class__.col1].index(key.value)
            self.sources[_DataKey.TABLE_CDS].data[self.__class__.col2][index_of_key] = value
        elif key is _DataKey.PLOT_CDS or key is _DataKey.TABLE_CDS:
            self.sources[key].data = value
        else:
            self.data[key] = value

    def update_limits(self, changed_aspect, new_value):
        """Preprocess and record an input value.
        
        Args:
            changed_aspect: input widget (String)
            new_value: input value (float)
        Returns:
            None
        """
        
        tools.print_fxn_name()
        if changed_aspect is _WidgetKey.Y_MAX_INPUT:
            value = min(np.float64(new_value), self.data[_DataKey.EXCEL_Y_MAX])
            self.set(key=_DataKey.PLOT_Y_MAX, value=value)
        elif changed_aspect is _WidgetKey.Y_MIN_INPUT:
            value = max(np.float64(new_value), self.data[_DataKey.EXCEL_Y_MIN])
            self.set(key=_DataKey.PLOT_Y_MIN, value=value)
        elif changed_aspect is _WidgetKey.X_MAX_INPUT:
            value = min(int(new_value), self.data[_DataKey.EXCEL_X_MAX])
            self.set(key=_DataKey.PLOT_X_MAX, value=value)
        elif changed_aspect is _WidgetKey.X_MIN_INPUT:
            value = max(int(new_value), self.data[_DataKey.EXCEL_X_MIN])
            self.set(key=_DataKey.PLOT_X_MIN, value=value)
        tools.print_fxn_name()
    
    def update_plot_cds(self):
        """Update the plot data.
        
        Args:
            None
        Returns:
            None
        """
        
        tools.print_fxn_name()
        # make cals
        constants_df = self.data[_DataKey.EXCEL_DF]
        new_plot_df = constants_df.iloc[self.data[_DataKey.PLOT_X_MIN]: self.data[_DataKey.PLOT_X_MAX] + 1, :]
        new_plot_df = new_plot_df[(new_plot_df[_JsonKey.Y_NAME.value] <= self.data[_DataKey.PLOT_Y_MAX]) & 
                                  (new_plot_df[_JsonKey.Y_NAME.value] >= self.data[_DataKey.PLOT_Y_MIN])]
        new_plot_dict = {_JsonKey.X_NAME.value: new_plot_df[_JsonKey.X_NAME.value].as_matrix(), 
                         _JsonKey.Y_NAME.value: new_plot_df[_JsonKey.Y_NAME.value].as_matrix()}
        # update source
        self.set(key=_DataKey.PLOT_CDS, value=new_plot_dict)
        tools.print_fxn_name() 
    
    def update_table_cds(self):
        """Update the table data.
        
        Args:
            None
        Returns:
            None
        """
        
        tools.print_fxn_name()
        # list commons
        y_axis = self.sources[_DataKey.PLOT_CDS].data[_JsonKey.Y_NAME.value]
        
        # make calcs
        table_dict = {self.__class__.col1: [_TableCdsKey.AVG.value,
                                            _TableCdsKey.CPK.value,
                                            _TableCdsKey.VAR_MAX.value,
                                            _TableCdsKey.VAR_MIN.value,
                                            _TableCdsKey.FAILS_NUM.value,
                                            _TableCdsKey.FAILS_RATIO.value],
                      self.__class__.col2: [_calc_average(y_axis), 
                                            _calc_cpk(y_axis, _JsonKey.LOWER_LIMIT.value, _JsonKey.UPPER_LIMIT.value), 
                                            _calc_variation_limits(y_axis)[1],
                                            _calc_variation_limits(y_axis)[0],
                                            _calc_failures(y_axis, _JsonKey.LOWER_LIMIT.value, _JsonKey.UPPER_LIMIT.value)[0],
                                            _calc_failures(y_axis, _JsonKey.LOWER_LIMIT.value, _JsonKey.UPPER_LIMIT.value)[1]]}
        # update sources                       
        self.set(key=_DataKey.TABLE_CDS, value=table_dict)
        tools.print_fxn_name()

class _VariationAnalysisFigure(object):
    pass
           
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
    tools.print_fxn_name()
    if string == "":
        return False
    
    try:
        float(string)
    except ValueError:
        tools.print_fxn_name()
        return False
    else:
        tools.print_fxn_name()
        return True
    
def _calc_average(data_set: pd.Series) -> float:
    """Calculate the average of a given data set.
    
    Args:
        data_set: data to use for average (Series)
    Returns:
        average (float)
    """
    
    tools.print_fxn_name()
    average = data_set.mean(axis=0)
    rounded_average = round(average, _JsonKey.PRECISION.value)

    tools.print_fxn_name()
    return rounded_average
    
def _calc_average_moving_range(data_set: pd.Series, subset_length: int) -> float:
    """Calculate the average mR of a given data set.
    
    Args:
        data_set: data to use for mR (Series)
        subset_length: length of data subsets to use (int)
    Returns:
        average mR (float)
    """
    
    tools.print_fxn_name()
    count = 0.0
    # data subsets to calculate mR on
    element_pairs = zip(data_set[:-(subset_length - 1)], data_set[(subset_length - 1):])
    # calculations
    for (left, right) in element_pairs:
        count += abs(left - right)
        
    result = count / (len(data_set) - (subset_length - 1))
    rounded_result = round(result, _JsonKey.PRECISION.value)
    tools.print_fxn_name()
    
    return rounded_result
    
def _calc_variation_limits(data_set: pd.Series) -> float:
    """Calculate the upper/lower range limits of a data set.
    
    Args:
        data_set: data to use for URL/LRL (Series)
    Returns:
        (upper, lower) (float 2-tuple)
    """
    
    tools.print_fxn_name()
    # calculate averages
    average = _calc_average(data_set)
    average_moving_range = _calc_average_moving_range(data_set, 2)
    
    # calculate limits
    upper_natural_process_limits = average + (2.66 * average_moving_range)
    lower_natural_process_limits = average - (2.66 * average_moving_range)
    
    result = (lower_natural_process_limits, upper_natural_process_limits)
    rounded_result = (round(result[0], _JsonKey.PRECISION.value), round(result[1], _JsonKey.PRECISION.value))
    
    tools.print_fxn_name()
    return rounded_result

def _calc_cpk(data_set: pd.Series, lower: float, upper: float) -> float:
    """Calculate the cpk of a given data set.
    
    Args:
        data_set: data to use (Series)
        lower: lower limit (float)
        upper: upper limit (float)
    Returns:
        cpk (float)
    """

    tools.print_fxn_name()
    arr = np.array([x for x in data_set]).ravel()
    sigma = np.std(arr)
    mean = np.mean(data_set)
    
    left = np.float64(upper - mean) / (3 * sigma)
    right = np.float64(mean - lower) / (3 * sigma)
    
    result = min(left, right)
    rounded_result = round(result, _JsonKey.PRECISION.value)
    
    tools.print_fxn_name()
    return rounded_result

def _calc_failures(data_set: pd.Series, lower: float, upper: float) -> typing.Tuple[float, float]:
    """Calculate the amount of values outside the limits.
    
    Args:
        data_set: data to use (Series)
        lower: lower limit (float)
        upper: upper limit (float)        
    Returns:
        (number, percent) (float 2-tuple)
    """
    
    tools.print_fxn_name()
    length = data_set.shape[0]
    count = 0.0
    for x in data_set:
        if x < lower or x > upper:
            count += 1
            
    result = (count, round(count * 100 / length, _JsonKey.PRECISION.value))
    rounded_result = (result[0], round(result[1], _JsonKey.PRECISION.value))
    
    tools.print_fxn_name()
    return rounded_result

def create_json_enum(json_file):
    """
    """
    
    tools.print_fxn_name()
    global _JsonKey
    
    with open(json_file, "r") as f:
        json_obj = json.load(f)
        _JsonKey = enum.Enum(value="_JsonKey", 
                              names={"PRECISION": json_obj["precision"],
                                     "DATA_SHEET_NAME": json_obj["data_sheet_name"],
                                     "TITLE": json_obj["title"],
                                     "UPPER_LIMIT": json_obj["upper_limit"],
                                     "LOWER_LIMIT": json_obj["lower_limit"],
                                     "Y_NAME": json_obj["y_name"],
                                     "X_NAME": json_obj["x_name"]})
    tools.print_fxn_name()
        
def _prepare_variation_analysis_data(file_path: str) -> _VariationAnalysisData:
    """Preprocess data for variation analysis.
    
    Args:
        file_path: excel file path (String)
    Returns:
        preprocessed data (_VariationAnalysisData)
    """
    
    tools.print_fxn_name()
    # update globals
    create_json_enum(_TEST_ARGV2)    
    
    # grab data
    data_df = pd.read_excel(io=file_path, sheetname=_JsonKey.DATA_SHEET_NAME.value)
    
    # clean variable data
    data_df = data_df.round(decimals={_JsonKey.Y_NAME.value: _JsonKey.PRECISION.value})
    data_df = data_df.drop_duplicates()
    data_df = data_df.sort_values(by=[_JsonKey.X_NAME.value, _JsonKey.Y_NAME.value])
    
    # stucture data
    preprocessed_data = _VariationAnalysisData(data_df=data_df)
    
    tools.print_fxn_name()
    return preprocessed_data
    
def _create_variation_analysis_UI(preprocessed_data):
    """Create the UI for variation analysis.
    
    Args:
        preprocessed_data: (_VariationAnalysisData)
    Returns:
        None
    """

    tools.print_fxn_name()
    # callbacks and misc functions 
    def configure_figure():
        # add tools
        # figure.add_tools(bkm.HoverTool(tooltips=[("x", "@{}".format(constant_data[_JsonKey.X_AXIS_KEY.value])), 
        #                                          ("y", "@{}".format(constant_data[_JsonKey.Y_AXIS_KEY.value])), 
        #                                          ("index", "$index")]))
        # add plot data glyphs
        figure.circle(x=_JsonKey.X_NAME.value, y=_JsonKey.Y_NAME.value, 
                    size = 5, fill_color = "white", source=preprocessed_data.get(key=_DataKey.PLOT_CDS), legend="points")
        figure.line(x=_JsonKey.X_NAME.value, y=_JsonKey.Y_NAME.value, source=preprocessed_data.get(key=_DataKey.PLOT_CDS), legend="lines")
        # add legend
        figure.legend.click_policy="hide"
        figure.legend.border_line_width = 3
        figure.legend.border_line_color = "navy" 
        figure.legend.background_fill_alpha = 0
    def edit_input_value(obj, changed_aspect):
        """Edit the input widget's value.
        
        Args:
            obj: 
            changed_aspect:
        Returns:
            None
        """
        tools.print_fxn_name()
        # change input visual if exceeding max/min
        if changed_aspect is _WidgetKey.Y_MAX_INPUT:
            obj.value = str(preprocessed_data.get(key=_DataKey.PLOT_Y_MAX))
        elif changed_aspect is _WidgetKey.Y_MIN_INPUT:
            obj.value = str(preprocessed_data.get(key=_DataKey.PLOT_Y_MIN))
        elif changed_aspect is _WidgetKey.X_MAX_INPUT:
            obj.value = str(preprocessed_data.get(key=_DataKey.PLOT_X_MAX)) 
        elif changed_aspect is _WidgetKey.X_MIN_INPUT:
            obj.value = str(preprocessed_data.get(key=_DataKey.PLOT_X_MIN))         
        tools.print_fxn_name()    
    def update_plot_lines():
        """Edit the plot's lines with _VariationAnalysisData.
        
        Args:
            None
        Returns:
            None
        """
        tools.print_fxn_name()
        average.location = preprocessed_data.get(key=_TableCdsKey.AVG)
        variation_max.location = preprocessed_data.get(key=_TableCdsKey.VAR_MAX)
        variation_min.location = preprocessed_data.get(key=_TableCdsKey.VAR_MIN) 
        tools.print_fxn_name() 
    def callback_text_input(attr, old, new, widget):
        """Process new input.
        
        Args:
            attr: changed widget attribute (String)
            old: old widget value (String)
            new: new widget value (String)
            widget: widget id (_WidgetKey)
        Returns:
            None
        """
        tools.print_fxn_name()

        obj = None
        if widget is _WidgetKey.Y_MAX_INPUT:
            obj = y_max_input
        elif widget is _WidgetKey.Y_MIN_INPUT:
            obj = y_min_input
        elif widget is _WidgetKey.X_MAX_INPUT:
            obj = x_max_input
        elif widget is _WidgetKey.X_MIN_INPUT:
            obj = x_min_input
            
        # terminate early
        if _is_string_number(new) is False:
            obj.value = old
            tools.print_fxn_name()
            return
        formatted_new = np.float("{:.3f}".format(np.float64(new)))
        if formatted_new == old:
            obj.value = old
            tools.print_fxn_name()
            return
        if widget is _WidgetKey.Y_MAX_INPUT:
            if formatted_new < preprocessed_data.get(key=_DataKey.PLOT_Y_MIN):
                obj.value = old
                tools.print_fxn_name()
                return
        elif widget is _WidgetKey.Y_MIN_INPUT:
            if formatted_new > preprocessed_data.get(key=_DataKey.PLOT_Y_MAX):
                obj.value = old
                tools.print_fxn_name()
                return
        elif widget is _WidgetKey.X_MAX_INPUT:
            if formatted_new < preprocessed_data.get(key=_DataKey.PLOT_X_MIN):
                obj.value = old
                tools.print_fxn_name()
                return
        elif widget is _WidgetKey.X_MIN_INPUT:
            if formatted_new > preprocessed_data.get(key=_DataKey.PLOT_X_MAX):
                obj.value = old
                tools.print_fxn_name()
                return
    
        # update data, plot, input widget, and output widget
        preprocessed_data.update_limits(changed_aspect=widget, new_value=formatted_new)
        preprocessed_data.update_plot_cds()
        preprocessed_data.update_table_cds()
        update_plot_lines()
        edit_input_value(obj=obj, changed_aspect=widget)
    # def callback_save_output():
    #     tools.create_timestamp(output_file_path)
    #     with open(output_file_path, "a") as f:
    #         dict = {"input": [(item, value[0]) for item, value in input_source.data.items() if len(value) == 1],
    #                 "output": [(item, value) for item, value in zip(output_data.data["calculation"], output_data.data["value"])]}
    #         JSON_STRING = json.dumps(dict, indent = 2, sort_keys = True)
    #         f.write(JSON_STRING + "\n\n")
    
    # init figure
    figure = bkp.figure(title=_JsonKey.TITLE.value,
                        x_axis_label=_JsonKey.X_NAME.value, 
                        y_axis_label=_JsonKey.Y_NAME.value, 
                        x_axis_type="datetime",
                        y_axis_type="linear",
                        plot_width=1200)
    # configure figure
    configure_figure()
    # add lines
    average = bkm.Span(dimension="width", line_color="#000000", line_dash="dashed",
                    location=preprocessed_data.get(key=_TableCdsKey.AVG), line_width=3)
    pass_fail_max = bkm.Span(dimension="width", line_color="#FF0000", line_dash="dashed",
                            location=_JsonKey.UPPER_LIMIT.value, line_width=3)
    pass_fail_min = bkm.Span(dimension="width", line_color="#FF0000", line_dash="dashed",
                            location=_JsonKey.LOWER_LIMIT.value, line_width=3)
    variation_max = bkm.Span(dimension="width", line_color="#FFA500", line_dash="dashed",
                            location=preprocessed_data.get(key=_TableCdsKey.VAR_MAX), line_width=3)
    variation_min = bkm.Span(dimension="width", line_color="#FFA500", line_dash="dashed",
                            location=preprocessed_data.get(key=_TableCdsKey.VAR_MIN), line_width=3)
    figure.add_layout(average)
    figure.add_layout(pass_fail_max)
    figure.add_layout(pass_fail_min)
    figure.add_layout(variation_max)
    figure.add_layout(variation_min)

    # init input widgets
    y_max_input = bkm.TextInput(title=_WidgetKey.Y_MAX_INPUT.value, 
                                value=str(preprocessed_data.get(key=_DataKey.EXCEL_Y_MAX)))
    y_min_input = bkm.TextInput(title=_WidgetKey.Y_MIN_INPUT.value, 
                                value=str(preprocessed_data.get(key=_DataKey.EXCEL_Y_MIN)))  
    x_max_input = bkm.TextInput(title=_WidgetKey.X_MAX_INPUT.value, 
                                value=str(preprocessed_data.get(key=_DataKey.EXCEL_X_MAX)))
    x_min_input = bkm.TextInput(title=_WidgetKey.X_MIN_INPUT.value, 
                                value=str(preprocessed_data.get(key=_DataKey.EXCEL_X_MIN)))
    save_data = bkm.Button(label="save data", button_type="success")
    # configure input widgets
    y_max_input.on_change("value", partial(callback_text_input, widget=_WidgetKey.Y_MAX_INPUT))
    y_min_input.on_change("value", partial(callback_text_input, widget=_WidgetKey.Y_MIN_INPUT))
    x_max_input.on_change("value", partial(callback_text_input, widget=_WidgetKey.X_MAX_INPUT))
    x_min_input.on_change("value", partial(callback_text_input, widget=_WidgetKey.X_MIN_INPUT))
    # save_data.on_click(callback_save_output)
    # add output widgets
    table_column1 = bkmw.TableColumn(field=_VariationAnalysisData.col1, 
                                     title=_WidgetKey.COL_NAME_OUTPUT.value, sortable=False)
    table_column2 = bkmw.TableColumn(field=_VariationAnalysisData.col2, 
                                     title=_WidgetKey.COL_VALUE_OUTPUT.value, sortable=False)
    table_output = bkmw.DataTable(source=preprocessed_data.get(key=_DataKey.TABLE_CDS), 
                                  columns=[table_column1, table_column2], 
                                  row_headers=False, sizing_mode="scale_width", fit_columns=False)    
    # configure layout
    input_left = bkl.column([y_max_input, y_min_input])
    input_right = bkl.column([x_max_input, x_min_input])
    text_input = bkl.row([input_left, input_right])
    input = bkl.column([text_input, save_data])
    widgets = bkl.row([input, table_output])
    plot_and_io = bkl.column([figure, widgets])
    bkio.curdoc().add_root(plot_and_io)

    tools.print_fxn_name()

#~~~~  PUBLIC FUNCTIONS  ~~~~#
def variation_analysis(file_path: str) -> None:
    """Perform and display a variation analysis.
    
    Args:
        file_path: excel file path (String)
    Returns:
        None
    """
    
    tools.print_fxn_name()
    preprocessed_data = _prepare_variation_analysis_data(file_path)
    _create_variation_analysis_UI(preprocessed_data)
    tools.print_fxn_name()

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