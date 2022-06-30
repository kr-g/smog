# from functools import reduce


import re


# for libxmp

_regex = re.compile(r"(\d+),(\d+\.\d+)([NESW])")


def split_coo(gpscoo):
    m = _regex.match(gpscoo)

    coo = float(m.group(1)), float(m.group(2)), m.group(3)
    # print(coo)
    return coo


def get_lat_lon_s(exif_gps_info):
    lats = exif_gps_info["GPSLatitude"]
    lons = exif_gps_info["GPSLongitude"]
    return (lats), (lons)


def split_lat_lon_v(lats, lons):
    latv = split_coo(lats)
    lonv = split_coo(lons)
    return (latv), (lonv)


def _conv_deg(val):
    divs = [1.0, 60.0]
    acc = 0
    for v, d in zip(val, divs):
        acc += v / d
    return acc


def get_lat_lon_degree(latv, lonv):

    lat = _conv_deg(latv[0:3])
    if latv[-1] != "N":
        lat = 0 - lat

    lon = _conv_deg(lonv[0:3])
    if lonv[-1] != "E":
        lon = 0 - lon

    return lat, lon


def get_lat_lon(gpsinfo):
    lats, lons = get_lat_lon_s(gpsinfo)
    latv, lonv = split_lat_lon_v(lats, lons)
    lat, lon = get_lat_lon_degree(latv, lonv)
    return lat, lon


# works with PIL exif tags
def _convert_degree(value):
    # print(value)
    divs = [1.0, 60.0, 3600.0]
    acc = 0
    for i, (v1, v2) in enumerate(value):
        acc += v1 / v2 / divs[i]
    return acc


def PIL_get_lat_lon(exif_gps_info):

    gps_lat = exif_gps_info.get("GPSLatitude")
    gps_lat_ref = exif_gps_info.get("GPSLatitudeRef")

    gps_long = exif_gps_info.get("GPSLongitude")
    gps_long_ref = exif_gps_info.get("GPSLongitudeRef")

    try:

        lat = _convert_degree(gps_lat)
        if gps_lat_ref != "N":
            lat = 0 - lat

        lon = _convert_degree(gps_long)
        if gps_long_ref != "E":
            lon = 0 - lon

        return lat, lon

    except Exception as ex:
        raise Exception(ex, "invalid input", exif_gps_info)
