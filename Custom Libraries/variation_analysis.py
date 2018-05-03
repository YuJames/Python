#!/usr/bin/env python3

"""Visualization of Data Variation.

This module uses Bokeh v.0.12.12 to perform an interactive variation analysis on
data.
    
ToDo:
    ~~~~NOW~~~~
    log preprocessing
    control data types better
    fix HoverTool
    ~~~~CONSIDERATION~~~~
    features: 
        input options: 
            sliders or textinput (how to handle y range select)
            prune outliers
        output options:
            add moving range graph
        process:
            more checks/preprocessing (json file, type check dataframe row)
    fixes:
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
import analysis_core as ac
import enum
import functools
import json
import logging
import math
import subprocess                               # not currently used
import sys
import time                                     # not currently used
import typing

import bokeh.client as bkc                      # not currently used
import bokeh.core.enums as bkce
import bokeh.io.doc as bkiod
import bokeh.layouts as bkl
import bokeh.models.annotations as bkma
import bokeh.models.sources as bkms
import bokeh.models.tools as bkmt
import bokeh.models.widgets.buttons as bkmwb
import bokeh.models.widgets.groups as bkmwg
import bokeh.models.widgets.inputs as bkmwi
import bokeh.models.widgets.sliders as bkmws
import bokeh.models.widgets.tables as bkmwt
import bokeh.plotting as bkp
import numpy as np
import pandas as pd
import tools

#~~~~  PRIVATE (GLOBAL CONSTANTS and ENUMS)  ~~~~#
class _DataKey(enum.Enum):
    """keys to access general data"""
    # static
    XCL_DF = "excel dataframe"
    XCL_Y_MAX = "excel y max"
    XCL_Y_MIN = "excel y min"
    XCL_X_MAX = "excel x max"
    XCL_X_MIN = "excel x min"
    # dynamic
    PLT_Y_MAX = "plot y max"
    PLT_Y_MIN = "plot y min"
    PLT_X_MAX = "plot x max"
    PLT_X_MIN = "plot x min"
    PLT_CDS = "plot source"
    TBL_CDS = "table source"
    
"""keys to access json data"""
_JsonKey = None

class _TableCdsKey(enum.Enum):
    """keys to access output data"""
    # general
    AVG = "average"
    PASS_MAX = "max passing threshold"
    PASS_MIN = "min passing threshold"
    FAIL_NUM = "failures (num)"
    FAIL_RATIO = "failures (%)"
    # analysis-specific
    CPK = "cpk"
    VAR_MAX = "max variation threshold"
    VAR_MIN = "min variation threshold"
    
class _WidgetKey(enum.Enum):
    """keys to access widgets"""
    # x inputs
    X_IN_PART = "X Partitions"
    X_IN_CURR = "X Current Partitions"
    X_IN_PREC = "X Precision"
    X_IN = "X Index Range"
    # y inputs
    Y_IN_PART = "Y Partitions"
    Y_IN_CURR = "Y Current Partitions"
    Y_IN_PREC = "Y Precision"
    Y_IN = "Y Value Range"
    # outputs
    COL_NAME_OUT = "Calculation"
    COL_VALUE_OUT = "Value"
    # checkboxes
    BOXES = "test title"
    GEN_BOX = "General Analysis"
    VAR_BOX = "Variation Analysis"

#~~~~  PUBLIC (GLOBAL CONSTANTS and ENUMS)  ~~~~#

#~~~~  PRIVATE GLOBAL VARIABLES  ~~~~#

#~~~~  PUBLIC GLOBAL VARIABLES  ~~~~#

#~~~~  PRIVATE CLASSES  ~~~~#
class _VariationAnalysisFigure(ac.AnalysisFigure):
    class _VariationAnalysisData(ac.AnalysisData): 
        def __init__(self, data):
            """Container for variation analysis data.
            
            Args:
                data: data to analyze (pd.DataFrame)
            Returns:
                None
            """
            
            super().__init__()
            
            y_axis = data.loc[:, _JsonKey.Y_NAME.value]
            x_axis = data.loc[:, _JsonKey.X_NAME.value]
            col_1_key = _WidgetKey.COL_NAME_OUT.value
            col_2_key = _WidgetKey.COL_VALUE_OUT.value
            
            # init sources
            table_dict = {col_1_key: [_TableCdsKey.AVG.value,
                                      _TableCdsKey.PASS_MAX.value,
                                      _TableCdsKey.PASS_MIN.value,
                                      _TableCdsKey.FAIL_NUM.value,
                                      _TableCdsKey.FAIL_RATIO.value,
                                      _TableCdsKey.CPK.value,
                                      _TableCdsKey.VAR_MAX.value,
                                      _TableCdsKey.VAR_MIN.value],
                          col_2_key: [ac.calc_avg(data=y_axis, prec=_JsonKey.PREC.value), 
                                      _JsonKey.PASS_MAX.value,
                                      _JsonKey.PASS_MIN.value,
                                      ac.calc_failures(data=y_axis, 
                                                       lower=_JsonKey.PASS_MIN.value, 
                                                       upper=_JsonKey.PASS_MAX.value,
                                                       prec=_JsonKey.PREC.value)[0],
                                      ac.calc_failures(data=y_axis, 
                                                       lower=_JsonKey.PASS_MIN.value, 
                                                       upper=_JsonKey.PASS_MAX.value,
                                                       prec=_JsonKey.PREC.value)[1],
                                      ac.calc_cpk(data=y_axis, 
                                                  lower=_JsonKey.PASS_MIN.value, 
                                                  upper=_JsonKey.PASS_MAX.value,
                                                  prec=_JsonKey.PREC.value), 
                                      ac.calc_var_limits(data=y_axis, prec=_JsonKey.PREC.value)[1],
                                      ac.calc_var_limits(data=y_axis, prec=_JsonKey.PREC.value)[0]]}
            self._sources[_DataKey.PLT_CDS] = bkms.ColumnDataSource(data=data)
            self._sources[_DataKey.TBL_CDS] = bkms.ColumnDataSource(data=table_dict)
                    
            # init data
            self._data[_DataKey.XCL_DF] = data
            self._data[_DataKey.XCL_Y_MAX] = y_axis.max()
            self._data[_DataKey.XCL_Y_MIN] = y_axis.min()
            self._data[_DataKey.XCL_X_MAX] = x_axis.size - 1
            self._data[_DataKey.XCL_X_MIN] = 0
            self._data[_DataKey.PLT_Y_MAX] = y_axis.max()
            self._data[_DataKey.PLT_Y_MIN] = y_axis.min()
            self._data[_DataKey.PLT_X_MAX] = x_axis.size - 1
            self._data[_DataKey.PLT_X_MIN] = 0
            
        def __getitem__(self, key):
            try:
                if key in _TableCdsKey:
                    print("first")
                    cds = self._sources[_DataKey.TBL_CDS]
                    print("second")
                    index_of_key = cds.data[_WidgetKey.COL_NAME_OUT.value].index(key.value)
                    print("third")
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
            except:
                print("in except")
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
            
            x_min = int(self._data[_DataKey.PLT_X_MIN])
            x_max = int(self._data[_DataKey.PLT_X_MAX])
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
        
        def update_table_cds(self, checkboxes):
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
            table_dict = {col_1_key: [], 
                          col_2_key: []}
            if 0 in checkboxes:
                table_dict[col_1_key].extend([_TableCdsKey.AVG.value, 
                                              _TableCdsKey.PASS_MAX.value, 
                                              _TableCdsKey.PASS_MIN.value])
                table_dict[col_2_key].extend([ac.calc_avg(data=y_axis, prec=_JsonKey.PREC.value), 
                                              _JsonKey.PASS_MAX.value, 
                                              _JsonKey.PASS_MIN.value]) 
            if 1 in checkboxes:
                table_dict[col_1_key].extend([_TableCdsKey.FAIL_NUM.value,
                                              _TableCdsKey.FAIL_RATIO.value,
                                              _TableCdsKey.CPK.value,
                                              _TableCdsKey.VAR_MAX.value,
                                              _TableCdsKey.VAR_MIN.value])
                table_dict[col_2_key].extend([ac.calc_failures(data=y_axis, 
                                                               lower=_JsonKey.PASS_MIN.value, 
                                                               upper=_JsonKey.PASS_MAX.value,
                                                               prec=_JsonKey.PREC.value)[0],
                                              ac.calc_failures(data=y_axis, 
                                                               lower=_JsonKey.PASS_MIN.value, 
                                                               upper=_JsonKey.PASS_MAX.value,
                                                               prec=_JsonKey.PREC.value)[1],
                                              ac.calc_cpk(data=y_axis, 
                                                          lower=_JsonKey.PASS_MIN.value, 
                                                          upper=_JsonKey.PASS_MAX.value,
                                                          prec=_JsonKey.PREC.value),
                                              ac.calc_var_limits(data=y_axis, 
                                                                 prec=_JsonKey.PREC.value)[1],
                                              ac.calc_var_limits(data=y_axis, 
                                                                 prec=_JsonKey.PREC.value)[0]])
                  
            self[_DataKey.TBL_CDS] = table_dict    
    
    def __init__(self, data):
        """Container for variation analysis.
        
        Args:
            data: data container (pd.DataFrame)
        Returns:
            None
        """
        
        super().__init__()
        
        self._data = self._VariationAnalysisData(data=data)
        self._figure = bkp.figure(title=_JsonKey.TITLE.value,
                                  x_axis_label=_JsonKey.X_NAME.value, 
                                  y_axis_label=_JsonKey.Y_NAME.value, 
                                  x_axis_type="datetime",
                                  y_axis_type="linear",
                                  plot_width=1200)
        # add tools
        self._figure.add_tools(bkmt.HoverTool(tooltips=[("x", "@{}".format(_JsonKey.X_NAME.value)), 
                                                        ("y", "@{}".format(_JsonKey.Y_NAME.value)), 
                                                        ("index", "$index")],
                                              formatters={"datetime": "datetime"}))
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
        _x_in_partitions = bkmws.Slider(title=_WidgetKey.X_IN_PART.value, 
                                        start=2, end=10, value=2, step=1)
        _x_in_current = bkmws.RangeSlider(title=_WidgetKey.X_IN_CURR.value, 
                                          start=1, end=2, step=1, value=(1,2))
        _x_in_precision = bkmwi.Select(title=_WidgetKey.X_IN_PREC.value, 
                                       options=["1", "10", "100"], value="1")
        _x_in = bkmws.RangeSlider(title=_WidgetKey.X_IN.value, start=self._data[_DataKey.XCL_X_MIN], 
                                  end=self._data[_DataKey.XCL_X_MAX], step=1, 
                                  value=(self._data[_DataKey.XCL_X_MIN], self._data[_DataKey.XCL_X_MAX]))
        _y_in_partitions = None
        _y_in_current = None
        _Y_IN_PREC = None
        _y_in = bkmws.RangeSlider(title=_WidgetKey.Y_IN.value, 
                                  start=self._data[_DataKey.XCL_Y_MIN], 
                                  end=self._data[_DataKey.XCL_Y_MAX], step=1, 
                                  value=(self._data[_DataKey.XCL_Y_MIN], self._data[_DataKey.XCL_Y_MAX]))
        # self._save_data = bkmwb.Button(label="save data", button_type="success")
        _x_in_partitions.on_change("value", functools.partial(self._cb_input_settings, widget=_x_in_partitions))
        _x_in_current.on_change("value", functools.partial(self._cb_input_settings, widget=_x_in_current))
        _x_in_precision.on_change("value", functools.partial(self._cb_input_settings, widget=_x_in_precision))
        _x_in.on_change("value", functools.partial(self._cb_input_settings, widget=_x_in))
        # _Y_IN_PREC.on_change("value", functools.partial(self._callback_select, widget=_Y_IN_PREC))
        # _y_in.on_change("value", functools.partial(self._callback_slider, widget=_y_in))
        # self._save_data.on_click(callback_save_output)
        in_table_display = bkmwg.CheckboxGroup(labels=[_WidgetKey.GEN_BOX.value, _WidgetKey.VAR_BOX.value], active=[0, 1], name=_WidgetKey.BOXES.value)
        in_table_display.on_click(self._cb_table_settings)
        
        # init output widgets
        _tbl_col1 = bkmwt.TableColumn(field=_WidgetKey.COL_NAME_OUT.value,
                                      title=_WidgetKey.COL_NAME_OUT.value)
        _tbl_col2 = bkmwt.TableColumn(field=_WidgetKey.COL_VALUE_OUT.value,
                                      title=_WidgetKey.COL_VALUE_OUT.value)
        _tbl_out = bkmwt.DataTable(source=self._data[_DataKey.TBL_CDS], 
                                   columns=[_tbl_col1, _tbl_col2], 
                                   fit_columns=False, row_headers=False, sizing_mode="scale_width",
                                   sortable=True, selectable=True, scroll_to_selection=True)    
        # init widgets
        self._widgets = {_WidgetKey.X_IN_PART: _x_in_partitions,
                         _WidgetKey.X_IN_CURR: _x_in_current,
                         _WidgetKey.X_IN_PREC: _x_in_precision,
                         _WidgetKey.X_IN: _x_in,
                         _WidgetKey.COL_NAME_OUT: _tbl_col1,
                         _WidgetKey.COL_VALUE_OUT: _tbl_col2,
                         _WidgetKey.BOXES: in_table_display}
                                                                
        # init layout
        input_left = bkl.column(children=[_x_in_partitions, _x_in_current, _x_in_precision, _x_in])
        input_right = bkl.column(children=[])
        text_input = bkl.row(children=[input_left, input_right])
        input = bkl.column(children=[text_input])
        widgets = bkl.row(children=[input, in_table_display, _tbl_out])
        plot_and_io = bkl.column(children=[self._figure, widgets])
        bkiod.curdoc().add_root(model=plot_and_io)
        
        self._flag = False

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
        
    def _update_limits(self):
        """Update data range with input widget values.
        
        Args:
            None
        Returns:
            None
        """
        
        x_min, x_max = self[_WidgetKey.X_IN].value
        self._data[_DataKey.PLT_X_MIN] = x_min
        self._data[_DataKey.PLT_X_MAX] = x_max
        
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
    
    def _cb_input_settings(self, attr, old, new, widget):
        """
        """
        
        widget_enum = _WidgetKey(widget.title)
        
        # terminate early
        if self._flag is True:
            return
        self._flag = True
        print("Callback from input: {}".format(widget.title))
        # get widgets
        partitions = self[_WidgetKey.X_IN_PART]
        current = self[_WidgetKey.X_IN_CURR]
        prec = self[_WidgetKey.X_IN_PREC]
        input = self[_WidgetKey.X_IN]
        
        # basic calcs
        print("basic calcs")
        size = math.floor((self._data[_DataKey.XCL_X_MAX] + 1) / partitions.value)
        remainder = (self._data[_DataKey.XCL_X_MAX] + 1) % partitions.value
        start_part, end_part = current.value        
        
        # interact with widgets
        print("interaction")
        if widget_enum == _WidgetKey.X_IN_PART:
            current.start = 1
            current.end = new
            current.value = (current.start, current.end)        
            prec.value = "1"
            input.start = 0
            input.end = self._data[_DataKey.XCL_X_MAX]
            input.step = 1
            input.value = (input.start, input.end)
        elif widget_enum == _WidgetKey.X_IN_CURR:
            prec.value = "1"
            # calcs
            input.start = size * (start_part - 1)
            if end_part == partitions.value:
                input.end = size * end_part + remainder - 1
            else:
                input.end = size * end_part - 1
            # calcs
            input.step = 1
            input.value = (input.start, input.end)
        elif widget_enum == _WidgetKey.X_IN_PREC:
            input.step = int(new)
            input.value = (input.start, input.end)
        elif widget_enum == _WidgetKey.X_IN:
            pass
        self._flag = False
        
        # data calcs
        self._update_limits()
        self._data.update_plot_cds()
        self._data.update_table_cds(list(self[_WidgetKey.BOXES].active))
        self._update_plot_lines()
    
    def _cb_table_settings(self, new):
        print("checkbox clicked: {}".format(new))    
        self._data.update_table_cds(tuple(new))
    # def callback_save_output():
    #     tools.create_timestamp(output_file_path)
    #     with open(output_file_path, "a") as f:
    #         dict = {"input": [(item, value[0]) for item, value in input_source.data.items() if len(value) == 1],
    #                 "output": [(item, value) for item, value in zip(output_data.data["calculation"], output_data.data["value"])]}
    #         JSON_STRING = json.dumps(dict, indent = 2, sort_keys = True)
    #         f.write(JSON_STRING + "\n\n")
            
#~~~~  PUBLIC CLASSES  ~~~~#

#~~~~  PRIVATE FUNCTIONS  ~~~~#
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
                             names={"XCL_FILE_PATH": json_obj["excel file path"],
                                    "LOG_FILE_PATH": json_obj["logging file path"],
                                    "PREC": json_obj["rounding precision"],
                                    "SHEET_NAME": json_obj["data sheet name"],
                                    "TITLE": json_obj["analysis title"],
                                    "PASS_MAX": json_obj["max passing value"],
                                    "PASS_MIN": json_obj["min passing value"],
                                    "Y_NAME": json_obj["y axis name"],
                                    "X_NAME": json_obj["x axis name"]})
        
def _prepare_variation_analysis_data(json_file_path: str):
    """Preprocess data for variation analysis.
    
    Args:
        json_file_path: json file path (str)
    Returns:
        preprocessed data (pd.DataFrame)
    """
    
    # update globals
    _create_json_enum(file_path=json_file_path)   
    
    # grab data
    data_df = pd.read_excel(io=_JsonKey.XCL_FILE_PATH.value, sheetname=_JsonKey.SHEET_NAME.value)
    
    # clean variable data
    data_df = data_df.dropna()
    data_df = data_df.round(decimals={_JsonKey.Y_NAME.value: _JsonKey.PREC.value})
    data_df = data_df.drop_duplicates()
    data_df = data_df.sort_values(by=[_JsonKey.X_NAME.value, _JsonKey.Y_NAME.value])
    
    return data_df
    
def _create_variation_analysis_UI(data) -> None:
    """Create the UI for variation analysis.
    
    Args:
        data: data container (pd.DataFrame)
    Returns:
        None
    """

    figure = _VariationAnalysisFigure(data=data)

#~~~~  PUBLIC FUNCTIONS  ~~~~#
def variation_analysis(json_file_path: str) -> None:
    """Perform and display a variation analysis.
    
    Args:
        json_file_path: json file path (str)
    Returns:
        None
    """
    
    preprocessed_data = _prepare_variation_analysis_data(json_file_path=json_file_path)
    _create_variation_analysis_UI(data=preprocessed_data)

#~~~~  MAIN  ~~~~#

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
