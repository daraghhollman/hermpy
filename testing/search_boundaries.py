import datetime as dt

import matplotlib as mpl
import matplotlib.pyplot as plt

from hermean_toolbelt import boundary_crossings

mpl.rcParams["font.size"] = 14


sun_crossings = boundary_crossings.Load_Crossings("../../sun_crossings.p")
philpott_crossings = boundary_crossings.Load_Crossings("../../philpott_crossings.p")

mp_in = philpott_crossings[philpott_crossings["type"] == "mp_in"]
mp_out = philpott_crossings[philpott_crossings["type"] == "mp_out"]
bs_in = philpott_crossings[philpott_crossings["type"] == "bs_in"]
bs_out = philpott_crossings[philpott_crossings["type"] == "bs_out"]

print(mp_out.iloc[10:20])
