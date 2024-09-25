"""
Reformats the Philpott+ (2020) boundary interval list
"""

import hermpy.boundary_crossings as boundaries

root_dir = "/home/daraghhollman/Main/mercury/"

boundaries.Reformat_Philpott(root_dir + "philpott_2020.csv", root_dir + "philpott_2020_reformatted.csv")
