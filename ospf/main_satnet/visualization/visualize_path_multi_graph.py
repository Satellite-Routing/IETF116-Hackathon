# MIT License
#
# Copyright (c) 2020 Debopam Bhattacherjee
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import math
import ephem
import pandas as pd
import os, sys
import csv
import numpy as np
try:
    from sat_path_viz_depends.scripts import util
except (ImportError, SystemError):
    import util

# Visualizes paths between endpoints at specific time instances

EARTH_RADIUS = 6378135.0 # WGS72 value; taken from https://geographiclib.sourceforge.io/html/NET/NETGeographicLib_8h_source.html

# CONSTELLATION GENERATION GENERAL CONSTANTS
ECCENTRICITY = 0.0000001  # Circular orbits are zero, but pyephem does not permit 0, so lowest possible value
ARG_OF_PERIGEE_DEGREE = 0.0
PHASE_DIFF = False
EPOCH = "2000-01-01 00:00:00"

# CONSTELLATION SPECIFIC PARAMETERS
# STARLINK 550
NAME = "virtual_satellite_200"

################################################################
# The below constants are taken from Starlink's FCC filing as below:
# [1]: https://fcc.report/IBFS/SAT-MOD-20190830-00087
################################################################

MEAN_MOTION_REV_PER_DAY = 15.19  # Altitude ~550 km
ALTITUDE_M = 700000  # Altitude ~550 km
SATELLITE_CONE_RADIUS_M = 940700 # From https://fcc.report/IBFS/SAT-MOD-20181108-00083/1569860.pdf (minimum angle of elevation: 25 deg)
MAX_GSL_LENGTH_M = math.sqrt(math.pow(SATELLITE_CONE_RADIUS_M, 2) + math.pow(ALTITUDE_M, 2))
MAX_ISL_LENGTH_M = 2 * math.sqrt(math.pow(EARTH_RADIUS + ALTITUDE_M, 2) - math.pow(EARTH_RADIUS + 80000, 2)) # ISLs are not allowed to dip below 80 km altitude in order to avoid weather conditions
NUM_ORBS = 20
NUM_SATS_PER_ORB = 10
INCLINATION_DEGREE = 65


# KUIPER 630
"""
NAME = "kuiper_630"

################################################################
# The below constants are taken from Kuiper's FCC filing as below:
# [1]: https://www.itu.int/ITU-R/space/asreceived/Publication/DisplayPublication/8716
################################################################

MEAN_MOTION_REV_PER_DAY = 14.80  # Altitude ~630 km
ALTITUDE_M = 630000  # Altitude ~630 km
SATELLITE_CONE_RADIUS_M = ALTITUDE_M / math.tan(math.radians(30.0))  # Considering an elevation angle of 30 degrees; possible values [1]: 20(min)/30/35/45
MAX_GSL_LENGTH_M = math.sqrt(math.pow(SATELLITE_CONE_RADIUS_M, 2) + math.pow(ALTITUDE_M, 2))
MAX_ISL_LENGTH_M = 2 * math.sqrt(math.pow(EARTH_RADIUS + ALTITUDE_M, 2) - math.pow(EARTH_RADIUS + 80000, 2))  # ISLs are not allowed to dip below 80 km altitude in order to avoid weather conditions
NUM_ORBS = 34
NUM_SATS_PER_ORB = 34
INCLINATION_DEGREE = 51.9
"""
current_path = os.getcwd()
print("current path: "+current_path)
# General files needed to generate visualizations; Do not change for different simulations
topFile = current_path + "/sat_path_viz_depends/static_html/top.html"
bottomFile = current_path+ "/sat_path_viz_depends/static_html/bottom.html"
city_detail_file = current_path + "/sat_path_viz_depends/city_detail.txt"

# Time in ms for which visualization will be generated
# GEN_TIME=46800  #ms
GEN_TIME = 300000 #ms

# Input file; Generated during simulation
# Note the file_name consists of the 2 city IDs being offset by the size of the constellation
# City IDs are available in the city_detail_file.
# If city ID is X (for Paris X = 24) and constellation is Starlink_550 (1584 satellites),
# then offset ID is 1584 + 24 = 1608.
path_file_csv = "../test_data/end_to_end/run/logs_ns3/burst_0_route_trace.csv"
# Output directory for creating visualization html files
OUT_DIR = current_path + "/output/sat_path_viz/"
OUT_HTML_FILE = []

sat_objs = []
city_details = {}
paths_over_time = []
COLORSETS = ['FF6666', '006699', 'FF9966', '339933', 'FFCC33', 'FF9900', '99CC33', '0099CC', '99CCCC', '33CC99']
def read_path_file():
    """
    read end-to-end path from specific  csv file
    return time array and path array
    """
    paths = []
    times = []
    with open(path_file_csv) as csvfile:
        csv_reader = csv.reader(csvfile)  # 使用csv.reader读取csvfile中的文件
        for row in csv_reader:            # 将csv 文件中的数据保存到data中
            # print(len(row))
            # print(row)
            times.append(row[2])           # 选择某一列加入到data数组中
            paths.append(row[3:len(row)])
    return times, paths
def generate_path_at_time():
    """
    Generates end-to-end path at specified time
    :return: HTML formatted string for visualization
    """
    viz_string = []
    global src_GS
    global dst_GS
    global paths_over_time
    global OUT_HTML_FILE
    global GEN_TIME
    times, paths = read_path_file()
    prev_path = []
    for i in range(len(paths)):
        if (np.array_equal(prev_path, paths[i])):
            continue
        prev_path = paths[i]
        paths_over_time.append((int(times[i]), paths[i]))
    SEL_PATH_TIME = 0
    SEL_PATH = []
    for pn in range(len(paths_over_time)):
        SEL_PATH = paths_over_time[pn][1]
        print(SEL_PATH)
        lineColor = COLORSETS[pn%len(COLORSETS)]
        SEL_PATH_TIME = paths_over_time[pn][0]/1000000
        OUT_HTML_FILE.append( OUT_DIR + NAME + "_path" + str(pn))
        viz_string.append("")
        shifted_epoch = (pd.to_datetime(EPOCH) + pd.to_timedelta(SEL_PATH_TIME, unit='ms')).strftime(format='%Y/%m/%d %H:%M:%S.%f')
        print(shifted_epoch)

        for i in range(len(sat_objs)):
            sat_objs[i]["sat_obj"].compute(shifted_epoch)
            viz_string[pn] += "var redSphere = viewer.entities.add({name : '', position: Cesium.Cartesian3.fromDegrees(" \
                     + str(math.degrees(sat_objs[i]["sat_obj"].sublong)) + ", " \
                     + str(math.degrees(sat_objs[i]["sat_obj"].sublat)) + ", "+str(sat_objs[i]["alt_km"]*1000)+"), "\
                     + "ellipsoid : {radii : new Cesium.Cartesian3(20000.0, 20000.0, 20000.0), "\
                     + "material : Cesium.Color.BLACK.withAlpha(1),}});\n"

        orbit_links = util.find_orbit_links(sat_objs, NUM_ORBS, NUM_SATS_PER_ORB)
        for key in orbit_links:
            sat1 = orbit_links[key]["sat1"]
            sat2 = orbit_links[key]["sat2"]
            viz_string[pn] += "viewer.entities.add({name : '', polyline: { positions: Cesium.Cartesian3.fromDegreesArrayHeights([" \
                      + str(math.degrees(sat_objs[sat1]["sat_obj"].sublong)) + "," \
                      + str(math.degrees(sat_objs[sat1]["sat_obj"].sublat)) + "," \
                      + str(sat_objs[sat1]["alt_km"] * 1000) + "," \
                      + str(math.degrees(sat_objs[sat2]["sat_obj"].sublong)) + "," \
                      + str(math.degrees(sat_objs[sat2]["sat_obj"].sublat)) + "," \
                      + str(sat_objs[sat2]["alt_km"] * 1000) + "]), " \
                      + "width: 0.5, arcType: Cesium.ArcType.NONE, " \
                      + "material: new Cesium.PolylineOutlineMaterialProperty({ " \
                      + "color: Cesium.Color.GREY.withAlpha(0.3), outlineWidth: 0, outlineColor: Cesium.Color.BLACK})}});"
        for p in range(len(SEL_PATH)):
            if p == 0:
                GS = int(SEL_PATH[p]) - NUM_ORBS*NUM_SATS_PER_ORB
                print(city_details[GS]["name"])

                OUT_HTML_FILE[pn] += "_"+city_details[GS]["name"]
                viz_string[pn] += "var redSphere = viewer.entities.add({name : '', position: Cesium.Cartesian3.fromDegrees(" \
                          + str(city_details[GS]["long_deg"]) + ", " \
                          + str(city_details[GS]["lat_deg"]) + ", " \
                          + str(city_details[GS]["alt_km"] * 1000) + "), " \
                          + "ellipsoid : {radii : new Cesium.Cartesian3(50000.0, 50000.0, 50000.0), " \
                          + "material : Cesium.Color.GREEN.withAlpha(1),}});\n"
                dst = int(SEL_PATH[p + 1])
                viz_string[pn] += "viewer.entities.add({name : '', polyline: { positions: Cesium.Cartesian3.fromDegreesArrayHeights([" \
                          + str(city_details[GS]["long_deg"]) + "," \
                          + str(city_details[GS]["lat_deg"]) + "," \
                          + str(city_details[GS]["alt_km"] * 1000) + "," \
                          + str(math.degrees(sat_objs[dst]["sat_obj"].sublong)) + "," \
                          + str(math.degrees(sat_objs[dst]["sat_obj"].sublat)) + "," \
                          + str(sat_objs[dst]["alt_km"] * 1000) + "]), " \
                          + "width: 3.0, arcType: Cesium.ArcType.NONE, " \
                          + "material: new Cesium.PolylineOutlineMaterialProperty({ " \
                          + "color: Cesium.Color.fromCssColorString('#" + str(lineColor) + "'), outlineWidth: 0, outlineColor: Cesium.Color.BLACK})}});"
            if p == len(SEL_PATH) - 1:
                GS = int(SEL_PATH[p]) - NUM_ORBS * NUM_SATS_PER_ORB
                print(city_details[GS]["name"])
                OUT_HTML_FILE[pn] += "_" + city_details[GS]["name"]
                viz_string[pn] += "var redSphere = viewer.entities.add({name : '', position: Cesium.Cartesian3.fromDegrees(" \
                          + str(city_details[GS]["long_deg"]) + ", " \
                          + str(city_details[GS]["lat_deg"]) + ", " \
                          + str(city_details[GS]["alt_km"] * 1000) + "), " \
                          + "ellipsoid : {radii : new Cesium.Cartesian3(50000.0, 50000.0, 50000.0), " \
                          + "material : Cesium.Color.GREEN.withAlpha(1),}});\n"
                src = int(SEL_PATH[p-1])
                viz_string[pn] += "viewer.entities.add({name : '', polyline: { positions: Cesium.Cartesian3.fromDegreesArrayHeights([" \
                          + str(city_details[GS]["long_deg"]) + "," \
                          + str(city_details[GS]["lat_deg"]) + "," \
                          + str(city_details[GS]["alt_km"] * 1000) + "," \
                          + str(math.degrees(sat_objs[src]["sat_obj"].sublong)) + "," \
                          + str(math.degrees(sat_objs[src]["sat_obj"].sublat)) + "," \
                          + str(sat_objs[src]["alt_km"] * 1000) + "]), " \
                          + "width: 3.0, arcType: Cesium.ArcType.NONE, " \
                          + "material: new Cesium.PolylineOutlineMaterialProperty({ " \
                          + "color: Cesium.Color.fromCssColorString('#" + str(lineColor) + "'), outlineWidth: 0, outlineColor: Cesium.Color.BLACK})}});"
            if 0 < p < len(SEL_PATH) - 2:
            #print(SEL_PATH[p], SEL_PATH[p+1])
                src = int(SEL_PATH[p])
                dst = int(SEL_PATH[p+1])
                viz_string[pn] += "viewer.entities.add({name : '', polyline: { positions: Cesium.Cartesian3.fromDegreesArrayHeights(["\
                          + str(math.degrees(sat_objs[src]["sat_obj"].sublong)) + ","\
                          + str(math.degrees(sat_objs[src]["sat_obj"].sublat)) + ","+str(sat_objs[src]["alt_km"]*1000)+","\
                          + str(math.degrees(sat_objs[dst]["sat_obj"].sublong)) + ","\
                          + str(math.degrees(sat_objs[dst]["sat_obj"].sublat)) + ","+str(sat_objs[dst]["alt_km"]*1000)+"]), "\
                          + "width: 3.0, arcType: Cesium.ArcType.NONE, "\
                          + "material: new Cesium.PolylineOutlineMaterialProperty({ "\
                          + "color: Cesium.Color.fromCssColorString('#" + str(lineColor) + "'), outlineWidth: 0,"\
                          + "outlineColor: Cesium.Color.BLACK})}});"
        OUT_HTML_FILE[pn] += "_"+str(int(SEL_PATH_TIME/1000))+".html"
    return viz_string


city_details = util.read_city_details(city_details, city_detail_file)
sat_objs = util.generate_sat_obj_list(
    NUM_ORBS,
    NUM_SATS_PER_ORB,
    EPOCH,
    PHASE_DIFF,
    INCLINATION_DEGREE,
    ECCENTRICITY,
    ARG_OF_PERIGEE_DEGREE,
    MEAN_MOTION_REV_PER_DAY,
    ALTITUDE_M
)
viz_string = generate_path_at_time()
for vs in range(len(viz_string)):
    util.write_viz_files(viz_string[vs], topFile, bottomFile, OUT_HTML_FILE[vs])
