import bokeh.models.sources as bkms
import pandas as pd
import enum
import traceback

class _CdsTableKey(enum.Enum):
    AVG = "average"
    CPK = "cpk"
    VAR_MAX = "variation_max"
    VAR_MIN = "variation_min"
    FAILS_NUM = "fails (num)"
    FAILS_RATIO = "fails (%)"
    
