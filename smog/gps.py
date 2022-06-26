from functools import reduce


def _convert_degree(value):
    divs = [1.0, 60.0, 3600.0]
    acc = 0
    for i, (v1, v2) in enumerate(value):
        acc += v1 / v2 / divs[i]
    return acc


def get_lat_lon(exif_gps_info):

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
        raise Exception(ex, "invalid input", gps_info)
