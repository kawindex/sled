import sys
import warnings


if sys.float_info.max_exp < 1024:
    warnings.warn(
        f"max float of {sys.float_info.max} may not fully cover "
        "the allowed range of Sled float (64-bit)"
    )

if sys.float_info.min_exp > -1021:
    warnings.warn(
        f"min float of {sys.float_info.min} may not fully cover "
        "the allowed range of Sled float (64-bit)"
    )
