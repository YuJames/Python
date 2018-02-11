#!/usr/bin/env python3

"""Bokeh data visualization.

This module uses Bokeh v.0.12.12 to create interactive web UIs for analyzing 
data. The purpose is to encourage statistical process control (SPC).

Arguments:
    argv[1]: excel file path
    argv[2]: config json file path
    argv[3]: saved data file path               # not currently used
    
ToDo:
    ~~~~NOW~~~~
    update all docstrings
    rename functions
    ~~~~CONSIDERATION~~~~
    add option to pick preprocessing steps
    update x inputs to sliders
    drop row in dataframe if not fitting a data type (type check)
    validity check json file 
    improve _callback_text_input
    change text input value to match closest value (not just if only exceeding max)
        e.g. with y values of [1, 3, 6], a "max y" input of 5 would change to 3
    add more checks/preprocessing
    fix "float division by zero error" (when sigma = 0)
        impossible? Give warning instead?
    Look into static type checking
        float vs np.float64
        work on class methods
    ~~~~PERIODICALLY~~~~
    improve docstrings
    improve modularity (globals, fxns, variables)
    improve naming
    return vs return None vs nothing
    
"""

#~~~~  IMPORTS  ~~~~#
import enum
import functools
import json
import subprocess                               # not currently used
import sys
import time                                     # not currently used
import typing

import bokeh.client as bkc                      # not currently used
import bokeh.io.doc as bkiod
import bokeh.layouts as bkl
import bokeh.models.annotations as bkma
import bokeh.models.sources as bkms
import bokeh.models.widgets.buttons as bkmwb
import bokeh.models.widgets.inputs as bkmwi
import bokeh.models.widgets.tables as bkmwt
import bokeh.plotting as bkp
import numpy as np
import pandas as pd
import tools

#~~~~  PRIVATE (GLOBAL CONSTANTS and ENUMS)  ~~~~#
class _DataKey(enum.Enum):
    # keys to access general data
    XCL_DF = "excel dataframe"
    PLT_CDS = "plot source"
    TBL_CDS = "table source"
    XCL_Y_MAX = "excel y max"
    XCL_Y_MIN = "excel y min"
    XCL_X_MAX = "excel x max"
    XCL_X_MIN = "excel x min"
    PLT_Y_MAX = "plot y max"
    PLT_Y_MIN = "plot y min"
    PLT_X_MAX = "plot x max"
    PLT_X_MIN = "plot x min"

# keys to access json data
_JsonKey = None

class _TableCdsKey(enum.Enum):
    # keys to access output data
    AVG = "average"
    CPK = "cpk"
    VAR_MAX = "max variation"
    VAR_MIN = "min variation"
    PASS_MAX = "max pass"
    PASS_MIN = "min pass"
    FAILS_NUM = "fails (num)"
    FAILS_RATIO = "fails (%)"
    
class _WidgetKey(enum.Enum):
    # keys to access widgets
    Y_MAX_IN = "Y Max Value (inclusive)"
    Y_MIN_IN = "Y Min Value (inclusive)"
    X_MAX_IN = "X Max Index (inclusive)"
    X_MIN_IN = "X Min Index (inclusive)"
    COL_NAME_OUT = "Calculation"
    COL_VALUE_OUT = "Value"
    
# script arguments for testing/development
_TEST_ARGV1 = r"C:\Users\Alfred\Documents\GitHub\Python\Custom Libraries\test_data.xlsx"
_TEST_ARGV2 = r"C:\Users\Alfred\Documents\GitHub\Python\Custom Libraries\test_config.json"

#~~~~  PUBLIC (GLOBAL CONSTANTS and ENUMS)  ~~~~#

#~~~~  PRIVATE GLOBAL VARIABLES  ~~~~#

#~~~~  PUBLIC GLOBAL VARIABLES  ~~~~#

#~~~~  PRIVATE CLASSES  ~~~~#
class _VariationAnalysisData(object): 
    def __init__(self, data):
        """Container for variation analysis data.
        
        Args:
            data: data to analyze (pd.DataFrame)
        Returns:
            None
        """

        y_axis = data.loc[:, _JsonKey.Y_NAME.value]
        x_axis = data.loc[:, _JsonKey.X_NAME.value]
        col_1_key = _WidgetKey.COL_NAME_OUT.value
        col_2_key = _WidgetKey.COL_VALUE_OUT.value
        
        # init sources
        table_dict = {col_1_key: [_TableCdsKey.AVG.value,
                                  _TableCdsKey.CPK.value,
                                  _TableCdsKey.VAR_MAX.value,
                                  _TableCdsKey.VAR_MIN.value,
                                  _TableCdsKey.PASS_MAX.value,
                                  _TableCdsKey.PASS_MIN.value,
                                  _TableCdsKey.FAILS_NUM.value,
                                  _TableCdsKey.FAILS_RATIO.value],
                      col_2_key: [_calc_avg(data=y_axis, rounding=True), 
                                  _calc_cpk(data=y_axis, 
                                            lower=_JsonKey.PASS_MIN.value, 
                                            upper=_JsonKey.PASS_MAX.value,
                                            rounding=True), 
                                  _calc_var_limits(data=y_axis, rounding=True)[1],
                                  _calc_var_limits(data=y_axis, rounding=True)[0],
                                  _JsonKey.PASS_MAX.value,
                                  _JsonKey.PASS_MIN.value,
                                  _calc_failures(data=y_axis, 
                                                 lower=_JsonKey.PASS_MIN.value, 
                                                 upper=_JsonKey.PASS_MAX.value,
                                                 rounding=True)[0],
                                  _calc_failures(data=y_axis, 
                                                 lower=_JsonKey.PASS_MIN.value, 
                                                 upper=_JsonKey.PASS_MAX.value,
                                                 rounding=True)[1]]}
        self._sources = {_DataKey.PLT_CDS: bkms.ColumnDataSource(data=data),
                         _DataKey.TBL_CDS: bkms.ColumnDataSource(data=table_dict)}
                         
        # init data
        self._data = {_DataKey.XCL_DF: data,
                      _DataKey.XCL_Y_MAX: y_axis.max(),
                      _DataKey.XCL_Y_MIN: y_axis.min(),
                      _DataKey.XCL_X_MAX: x_axis.size - 1,
                      _DataKey.XCL_X_MIN: 0,
                      _DataKey.PLT_Y_MAX: y_axis.max(),
                      _DataKey.PLT_Y_MIN: y_axis.min(),
                      _DataKey.PLT_X_MAX: x_axis.size - 1,
                      _DataKey.PLT_X_MIN: 0}
            
    def __getitem__(self, key):
        if key in _TableCdsKey:
            cds = self._sources[_DataKey.TBL_CDS]
            index_of_key = cds.data[_WidgetKey.COL_NAME_OUT.value].index(key.value)
            value_at_index = cds.data[_WidgetKey.COL_VALUE_OUT.value][index_of_key]
            return value_at_index
        elif key is _DataKey.PLT_CDS or key is _DataKey.TBL_CDS:
            value_at_index = self._sources[key]
            return value_at_index
        elif key in _DataKey:
            value_at_index = self._data[key]
            return value_at_index
        else:
            self.__missing__(key)
            return None
                
    def __setitem__(self, key, value):
        if key in _TableCdsKey:
            cds = self._sources[_DataKey.TBL_CDS]
            index_of_key = cds.data[_WidgetKey.COL_NAME_OUT.value].index(key.value)
            cds.data[_WidgetKey.COL_VALUE_OUT.value][index_of_key] = value
        elif key is _DataKey.PLT_CDS or key is _DataKey.TBL_CDS:
            self._sources[key].data = value
        elif key in _DataKey:
            self._data[key] = value
        else:
            self.__missing__(key)
            
    def __missing__(self, key):
        print("Class {} does not use key '{}'.".format(self.__class__, key))

    def __repr__(self):
        result = ""

        result += "Class: {}\n".format(self.__class__.__name__)
        # result += "Sources\n"
        result += "Data\n"
        for key, val in self._data.items():
            if key is not _DataKey.XCL_DF:
                result += "  {}: {}\n".format(key, val)
                
        return result
        
    def update_plot_cds(self):
        """Update plot source based on current data.
        
        Args:
            None
        Returns:
            None
        """
        
        x_min = self._data[_DataKey.PLT_X_MIN]
        x_max = self._data[_DataKey.PLT_X_MAX]
        y_min = self._data[_DataKey.PLT_Y_MIN]
        y_max = self._data[_DataKey.PLT_Y_MAX]
        col_x_key = _JsonKey.X_NAME.value
        col_y_key = _JsonKey.Y_NAME.value
        
        # filter source
        xcl_df = self[_DataKey.XCL_DF]
        new_df = xcl_df.iloc[x_min: x_max + 1, :]
        y_axis = new_df[_JsonKey.Y_NAME.value]
        new_df = new_df[(y_axis <= y_max) & (y_axis >= y_min)]
        # update source
        new_dict = {col_x_key: new_df[_JsonKey.X_NAME.value].as_matrix(), 
                    col_y_key: new_df[_JsonKey.Y_NAME.value].as_matrix()}
        self[_DataKey.PLT_CDS] = new_dict
    
    def update_table_cds(self):
        """Update table source based on current data.
        
        Args:
            None
        Returns:
            None
        """
        
        y_axis = self._sources[_DataKey.PLT_CDS].data[_JsonKey.Y_NAME.value]
        col_1_key = _WidgetKey.COL_NAME_OUT.value
        col_2_key = _WidgetKey.COL_VALUE_OUT.value
        
        # update source
        table_dict = {col_1_key: [_TableCdsKey.AVG.value,
                                  _TableCdsKey.CPK.value,
                                  _TableCdsKey.VAR_MAX.value,
                                  _TableCdsKey.VAR_MIN.value,
                                  _TableCdsKey.PASS_MAX.value,
                                  _TableCdsKey.PASS_MIN.value,
                                  _TableCdsKey.FAILS_NUM.value,
                                  _TableCdsKey.FAILS_RATIO.value],
                      col_2_key: [_calc_avg(data=y_axis, rounding=True), 
                                  _calc_cpk(data=y_axis, 
                                            lower=_JsonKey.PASS_MIN.value, 
                                            upper=_JsonKey.PASS_MAX.value,
                                            rounding=True), 
                                  _calc_var_limits(data=y_axis, rounding=True)[1],
                                  _calc_var_limits(data=y_axis, rounding=True)[0],
                                  _JsonKey.PASS_MAX.value,
                                  _JsonKey.PASS_MIN.value,
                                  _calc_failures(data=y_axis, 
                                                 lower=_JsonKey.PASS_MIN.value, 
                                                 upper=_JsonKey.PASS_MAX.value,
                                                 rounding=True)[0],
                                  _calc_failures(data=y_axis, 
                                                 lower=_JsonKey.PASS_MIN.value, 
                                                 upper=_JsonKey.PASS_MAX.value,
                                                 rounding=True)[1]]}                    
        self[_DataKey.TBL_CDS] = table_dict
        
class _VariationAnalysisFigure(object):
    def __init__(self, data):
        """Container for variation analysis.
        
        Args:
            data: data container (_VariationAnalysisData)
        Returns:
            None
        """
        
        self._data = data
        self._figure = bkp.figure(title=_JsonKey.TITLE.value,
                                  x_axis_label=_JsonKey.X_NAME.value, 
                                  y_axis_label=_JsonKey.Y_NAME.value, 
                                  x_axis_type="datetime",
                                  y_axis_type="linear",
                                  plot_width=1200)
        # add tools
        # figure.add_tools(bkm.HoverTool(tooltips=[("x", "@{}".format(constant_data[_JsonKey.X_AXIS_KEY.value])), 
        #                                          ("y", "@{}".format(constant_data[_JsonKey.Y_AXIS_KEY.value])), 
        #                                          ("index", "$index")]))
        # add plot data glyphs
        self._figure.circle(x=_JsonKey.X_NAME.value, y=_JsonKey.Y_NAME.value, 
                            fill_color="white", legend="points", size=5, 
                            source=self._data[_DataKey.PLT_CDS])
        self._figure.line(x=_JsonKey.X_NAME.value, y=_JsonKey.Y_NAME.value, 
                          legend="lines", source=self._data[_DataKey.PLT_CDS])
        # add legend
        self._figure.legend.background_fill_alpha = 0
        self._figure.legend.border_line_color = "navy" 
        self._figure.legend.border_line_width = 3
        self._figure.legend.click_policy="hide"
        
        # init lines
        _avg = bkma.Span(dimension="width", line_color="#000000", line_dash="dashed", 
                         line_width=3, location=self._data[_TableCdsKey.AVG])
        _pass_min = bkma.Span(dimension="width", line_color="#FF0000", line_dash="dashed", 
                              line_width=3, location=_JsonKey.PASS_MIN.value)
        _pass_max = bkma.Span(dimension="width", line_color="#FF0000", line_dash="dashed",
                              line_width=3, location=_JsonKey.PASS_MAX.value)
        _var_min = bkma.Span(dimension="width", line_color="#FFA500", line_dash="dashed",
                             line_width=3, location=self._data[_TableCdsKey.VAR_MIN])
        _var_max = bkma.Span(dimension="width", line_color="#FFA500", line_dash="dashed", 
                             line_width=3, location=self._data[_TableCdsKey.VAR_MAX])
        self._figure.add_layout(obj=_avg)
        self._figure.add_layout(obj=_pass_max)
        self._figure.add_layout(obj=_pass_min)
        self._figure.add_layout(obj=_var_max)
        self._figure.add_layout(obj=_var_min)
        self._annotations = {_TableCdsKey.AVG: _avg,
                             _TableCdsKey.VAR_MAX: _var_max,
                             _TableCdsKey.VAR_MIN: _var_min,
                             _TableCdsKey.PASS_MAX: _pass_max,
                             _TableCdsKey.PASS_MIN: _pass_min}

        # init input widgets
        x_min_default = str(object=self._data[_DataKey.XCL_X_MIN])
        x_max_default = str(object=self._data[_DataKey.XCL_X_MAX])
        y_min_default = str(object=self._data[_DataKey.XCL_Y_MIN])
        y_max_default = str(object=self._data[_DataKey.XCL_Y_MAX])
        _x_min_in = bkmwi.TextInput(title=_WidgetKey.X_MIN_IN.value, value=x_min_default)
        _x_max_in = bkmwi.TextInput(title=_WidgetKey.X_MAX_IN.value, value=x_max_default)
        _y_min_in = bkmwi.TextInput(title=_WidgetKey.Y_MIN_IN.value, value=y_min_default)  
        _y_max_in = bkmwi.TextInput(title=_WidgetKey.Y_MAX_IN.value, value=y_max_default)
        # self._save_data = bkmwb.Button(label="save data", button_type="success")
        _x_min_in.on_change("value", functools.partial(self._callback_text_input, widget=_x_min_in))        
        _x_max_in.on_change("value", functools.partial(self._callback_text_input, widget=_x_max_in))
        _y_min_in.on_change("value", functools.partial(self._callback_text_input, widget=_y_min_in))
        _y_max_in.on_change("value", functools.partial(self._callback_text_input, widget=_y_max_in))
        # self._save_data.on_click(callback_save_output)
        # init output widgets
        _tbl_col1 = bkmwt.TableColumn(field=_WidgetKey.COL_NAME_OUT.value, sortable=False,
                                      title=_WidgetKey.COL_NAME_OUT.value)
        _tbl_col2 = bkmwt.TableColumn(field=_WidgetKey.COL_VALUE_OUT.value, sortable=False,
                                      title=_WidgetKey.COL_VALUE_OUT.value)
        _tbl_out = bkmwt.DataTable(source=self._data[_DataKey.TBL_CDS], 
                                   columns=[_tbl_col1, _tbl_col2], 
                                   fit_columns=False, row_headers=False, sizing_mode="scale_width")    
        # init widgets
        self._widgets = {_WidgetKey.X_MIN_IN: _x_min_in,
                         _WidgetKey.X_MAX_IN: _x_max_in,
                         _WidgetKey.Y_MIN_IN: _y_min_in,
                         _WidgetKey.Y_MAX_IN: _y_max_in,
                         _WidgetKey.COL_NAME_OUT: _tbl_col1,
                         _WidgetKey.COL_VALUE_OUT: _tbl_col2}
                                                                
        # init layout
        input_left = bkl.column(children=[_y_max_in, _y_min_in])
        input_right = bkl.column(children=[_x_max_in, _x_min_in])
        text_input = bkl.row(children=[input_left, input_right])
        # input = bkl.column(children=[text_input, self._save_data])
        input = bkl.column(children=[text_input])
        widgets = bkl.row(children=[input, _tbl_out])
        plot_and_io = bkl.column(children=[self._figure, widgets])
        bkiod.curdoc().add_root(model=plot_and_io)

    def __getitem__(self, key):
        if key in _WidgetKey:
            return self._widgets[key]
        elif key in _TableCdsKey:
            return self._annotations[key]
    
    def __setitem__(self, key, value):
        if key in _WidgetKey:
            self._widgets[key].value = value
        elif key in _TableCdsKey:
            self._annotations[key].location = value
        
    def _update_limits(self, widget):
        """Process and record an input widget value.
        
        Args:
            widget: input widget (bkmwi.TextInput)
        Returns:
            None
        """
        
        title_enum = _WidgetKey(widget.title)
        value = widget.value
        
        if title_enum == _WidgetKey.X_MIN_IN:
            # avoid lesser than min x value
            x_min = max(int(value), self._data[_DataKey.XCL_X_MIN])
            self._data[_DataKey.PLT_X_MIN] = x_min
        elif title_enum == _WidgetKey.X_MAX_IN:
            # avoid greater than max x value
            x_max = min(int(value), self._data[_DataKey.XCL_X_MAX])
            self._data[_DataKey.PLT_X_MAX] = x_max
        elif title_enum == _WidgetKey.Y_MIN_IN:
            # avoid lesser than min y value
            y_min = max(np.float64(value), self._data[_DataKey.XCL_Y_MIN])
            self._data[_DataKey.PLT_Y_MIN] = y_min
        elif title_enum == _WidgetKey.Y_MAX_IN:
            # avoid greater than max y value
            y_max = min(np.float64(value), self._data[_DataKey.XCL_Y_MAX])
            self._data[_DataKey.PLT_Y_MAX] = y_max
        
    def _update_plot_lines(self):
        """Update the horizontal plot lines based on current data.
        
        Args:
            None
        Returns:
            None
        """

        self[_TableCdsKey.AVG] = self._data[_TableCdsKey.AVG]
        self[_TableCdsKey.VAR_MAX] = self._data[_TableCdsKey.VAR_MAX]
        self[_TableCdsKey.VAR_MIN] = self._data[_TableCdsKey.VAR_MIN] 

    def _edit_input_value(self, widget):
        """Edit the input widget's visual value based on current data.
        
        Args:
            widget: input widget (bkmwi.TextInput)
        Returns:
            None
        """

        title_enum = _WidgetKey(widget.title)
        new_value = None
        
        # change input visual if exceeding max/min
        if title_enum is _WidgetKey.X_MIN_IN:
            new_value = str(object=self._data[_DataKey.PLT_X_MIN])
        elif title_enum is _WidgetKey.X_MAX_IN:
            new_value = str(object=self._data[_DataKey.PLT_X_MAX])
        elif title_enum is _WidgetKey.Y_MIN_IN:
            new_value = str(object=self._data[_DataKey.PLT_Y_MIN])     
        elif title_enum is _WidgetKey.Y_MAX_IN:
            new_value = str(object=self._data[_DataKey.PLT_Y_MAX])
        
        self[title_enum] = new_value
        
    def _callback_text_input(self, attr, old, new, widget):
        """Process new input.
        
        Args:
            attr: changed widget attribute (str)
            old: old widget value (str)
            new: new widget value (str)
            widget: input widget (bkmwi.TextInput)
        Returns:
            None
        """

        title_enum = _WidgetKey(widget.title)
        
        # terminate early
        if _is_string_number(new) is False:
            self[title_enum] = old
            return
        formatted_new = np.float("{:.3f}".format(np.float64(new)))
        if (formatted_new == old or
            title_enum is _WidgetKey.Y_MAX_IN and formatted_new < self._data[_DataKey.PLT_Y_MIN] or
            title_enum is _WidgetKey.Y_MIN_IN and formatted_new > self._data[_DataKey.PLT_Y_MAX] or
            title_enum is _WidgetKey.X_MAX_IN and formatted_new < self._data[_DataKey.PLT_X_MIN] or
            title_enum is _WidgetKey.X_MIN_IN and formatted_new > self._data[_DataKey.PLT_X_MAX]):
                self[title_enum] = old
                return
    
        # update data, plot, input widget, and output widget
        self._update_limits(widget=widget)
        self._data.update_plot_cds()
        self._data.update_table_cds()
        self._update_plot_lines()
        self._edit_input_value(widget=widget)
        
    # def callback_save_output():
    #     tools.create_timestamp(output_file_path)
    #     with open(output_file_path, "a") as f:
    #         dict = {"input": [(item, value[0]) for item, value in input_source.data.items() if len(value) == 1],
    #                 "output": [(item, value) for item, value in zip(output_data.data["calculation"], output_data.data["value"])]}
    #         JSON_STRING = json.dumps(dict, indent = 2, sort_keys = True)
    #         f.write(JSON_STRING + "\n\n")
            
#~~~~  PUBLIC CLASSES  ~~~~#

#~~~~  PRIVATE FUNCTIONS  ~~~~#
def _is_string_number(data: str) -> bool:
    """Check if string contents represent a number.
    
    Args:
        data: data to analyze (str)
    Returns:
        result of check (bool)
    """
    
    # terminate early
    if data == "":
        return False
    
    try:
        float(data)
    except ValueError:
        return False
    else:
        return True
    
def _calc_avg(data: pd.Series, rounding=False) -> float:
    """Calculate average.
    
    Args:
        data: data to analyze (pd.Series)
        rounding: use rounding (bool)
    Returns:
        average (float)
    """
    
    average = data.mean(axis=0)
    if rounding is True:
        average = round(number=average, ndigits=_JsonKey.PRECISION.value)

    return average
    
def _calc_avg_moving_range(data: pd.Series, length: int, rounding=False) -> float:
    """Calculate average mR.
    
    Args:
        data: data to analyze (pd.Series)
        length: length of data subsets (int)
        rounding: use rounding (bool)
    Returns:
        average mR (float)
    """
    
    count = 0.0
    # data subsets to calculate mR on
    element_pairs = zip(data[:-(length - 1)], data[(length - 1):])
    # calculations
    for (left, right) in element_pairs:
        count += abs(left - right)
        
    result = count / (len(data) - (length - 1))
    if rounding is True:
        result = round(number=result, ndigits=_JsonKey.PRECISION.value)
    
    return result
    
def _calc_var_limits(data: pd.Series, rounding=False) -> typing.Tuple[float, float]:
    """Calculate upper/lower range limits.
    
    Args:
        data: data to analyze (pd.Series)
        rounding: use rounding (bool)
    Returns:
        (upper, lower) (float 2-tuple)
    """
    
    # calculate averages
    average = _calc_avg(data=data, rounding=True)
    average_moving_range = _calc_avg_moving_range(data=data, length=2, rounding=True)
    
    # calculate limits
    upper_natural_process_limits = average + (2.66 * average_moving_range)
    lower_natural_process_limits = average - (2.66 * average_moving_range)
    
    result = (lower_natural_process_limits, upper_natural_process_limits)
    if rounding is True:
        result = (round(number=result[0], ndigits=_JsonKey.PRECISION.value), 
                  round(number=result[1], ndigits=_JsonKey.PRECISION.value))
    
    return result

def _calc_cpk(data: pd.Series, lower: float, upper: float, rounding=False) -> float:
    """Calculate cpk (capability statistics).
    
    Args:
        data: data to analyze (pd.Series)
        lower: lower limit (float)
        upper: upper limit (float)
        rounding: use rounding (bool)
    Returns:
        cpk (float)
    """

    arr = np.array(object=[x for x in data]).ravel()
    sigma = np.std(a=arr)
    mean = np.mean(a=data)
    
    left = np.float64(upper - mean) / (3 * sigma)
    right = np.float64(mean - lower) / (3 * sigma)
    
    result = min(left, right)
    if rounding is True:
        result = round(number=result, ndigits=_JsonKey.PRECISION.value)
    
    return result

def _calc_failures(data: pd.Series, lower: float, upper: float, rounding=False) -> typing.Tuple[float, float]:
    """Calculate failures.
    
    Args:
        data: data to analyze (pd.Series)
        lower: lower limit (float)
        upper: upper limit (float)    
        rounding: use rounding (bool)    
    Returns:
        (number, percent) (float 2-tuple)
    """
    
    length = data.shape[0]
    count = 0.0
    for x in data:
        if x < lower or x > upper:
            count += 1
            
    result = (count, round(number=count * 100 / length, ndigits=_JsonKey.PRECISION.value))
    if rounding is True:
        result = (result[0], round(number=result[1], ndigits=_JsonKey.PRECISION.value))

    return result

def _create_json_enum(file_path: str) -> None:
    """Parse configuration json file.
    
    Args:
        file_path: json file path (str)
    Returns:
        None
    """

    global _JsonKey
    
    with open(file=file_path, mode="r") as f:
        json_obj = json.load(fp=f)
        _JsonKey = enum.Enum(value="_JsonKey", 
                             names={"PRECISION": json_obj["rounding precision"],
                                    "SHEET_NAME": json_obj["data sheet name"],
                                    "TITLE": json_obj["analysis title"],
                                    "PASS_MAX": json_obj["max passing value"],
                                    "PASS_MIN": json_obj["min passing value"],
                                    "Y_NAME": json_obj["y axis name"],
                                    "X_NAME": json_obj["x axis name"]})
        
def _prepare_variation_analysis_data(file_path: str) -> _VariationAnalysisData:
    """Preprocess data for variation analysis.
    
    Args:
        file_path: excel file path (str)
    Returns:
        preprocessed data (_VariationAnalysisData)
    """
    
    # update globals
    _create_json_enum(file_path=_TEST_ARGV2)    
    
    # grab data
    data_df = pd.read_excel(io=file_path, sheetname=_JsonKey.SHEET_NAME.value)
    
    # clean variable data
    data_df = data_df.dropna()
    data_df = data_df.round(decimals={_JsonKey.Y_NAME.value: _JsonKey.PRECISION.value})
    data_df = data_df.drop_duplicates()
    data_df = data_df.sort_values(by=[_JsonKey.X_NAME.value, _JsonKey.Y_NAME.value])
    
    # stucture data
    preprocessed_data = _VariationAnalysisData(data=data_df)
    
    return preprocessed_data
    
def _create_variation_analysis_UI(data: _VariationAnalysisData) -> None:
    """Create the UI for variation analysis.
    
    Args:
        data: data container (_VariationAnalysisData)
    Returns:
        None
    """

    figure = _VariationAnalysisFigure(data=data)

#~~~~  PUBLIC FUNCTIONS  ~~~~#
def variation_analysis(file_path: str) -> None:
    """Perform and display a variation analysis.
    
    Args:
        file_path: excel file path (str)
    Returns:
        None
    """
    
    preprocessed_data = _prepare_variation_analysis_data(file_path=file_path)
    _create_variation_analysis_UI(data=preprocessed_data)

#~~~~  MAIN  ~~~~#
variation_analysis(_TEST_ARGV1)

#~~~~  DEAD CODE  ~~~~#

# def _filter_out_nonnumbers(data_set):
#     """Filter out non-number data _set elements.
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