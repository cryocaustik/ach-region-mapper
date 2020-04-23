import geopandas
from pathlib import Path
import json

BASE_DIR = Path("/mnt/c/dev/ach_regions")
REGION_MAP_PATH = BASE_DIR / "data/regions.json"
COUNTIES_SHAPE_ZIP_PATH = "zip:///" + str(BASE_DIR / "data/WA_County_Boundaries.zip")
REGION_DICT = None
COUNTY_DICT = None


def get_region(county, refresh=False):
    """Look up and return ACH region name using given county.

    Arguments:
        county {str} -- County Name (title case)

    Keyword Arguments:
        refresh {bool} -- Reloads region map on this run. (default: {False})

    Returns:
        str -- ACH region name
    """
    global REGION_DICT
    if not REGION_DICT or refresh:
        REGION_DICT = json.load(open(REGION_MAP_PATH))

    return REGION_DICT[county]


def get_county(region):
    """Look up and return County name using a reverse mapping of the ACH region dictionary.

    Arguments:
        region {str} -- ACH region name

    Returns:
        str -- County name
    """
    global COUNTY_DICT
    global REGION_DICT
    if not COUNTY_DICT:
        if not REGION_DICT:
            get_region("King")

        COUNTY_DICT = dict()
        for c, r in REGION_DICT.items():
            if r not in COUNTY_DICT:
                COUNTY_DICT[r] = c
                continue
            COUNTY_DICT[r] += f",{c}"

    return COUNTY_DICT[region]


def load_counties():
    """Load and return counties from specified GIS Shape zip.

    Returns:
        GeoDataFrame -- Counties GeoDataFrame.
    """
    counties = geopandas.read_file(COUNTIES_SHAPE_ZIP_PATH)
    return counties


def add_regions(counties):
    """Add ACH regions series to GeoDataFrame.

    Arguments:
        counties {GeoDataFrame} -- Counties GeoDataFrame

    Returns:
        GeoDataFrame -- Counties GeoDataFrame with ACH region series added.
    """
    counties["region"] = counties.apply(lambda c: get_region(c.JURISDIC_2), axis=1)
    return counties


def dissolve_counties(counties, by="region"):
    """Dissolve county polygons into single polygon based on specified 'by' column.
    (e.g. by='region' will group by and dissolve all rows by unique region field values.)

    Arguments:
        counties {GeoDataFrame} -- Counties GeoDataFrame to map regions onto.

    Keyword Arguments:
        by {str} -- Name of field to dissolve by (default: {"region"})

    Returns:
        GeoDataFrame -- Dissolved GeoDataFrame.
    """
    dissolved = counties.dissolve(by=by)
    dissolved.reset_index(inplace=True)
    dissolved["counties"] = dissolved.apply(lambda r: get_county(r.region), axis=1)
    dissolved.drop(
        [
            "OBJECTID",
            "JURISDICT_",
            "JURISDIC_1",
            "JURISDIC_2",
            "JURISDIC_3",
            "JURISDIC_4",
            "JURISDIC_5",
            "JURISDIC_6",
            "EDIT_STATU",
            "EDIT_WHO",
        ],
        axis=1,
        inplace=True,
    )
    return dissolved


def export_geojson(counties, path):
    """Exports GeoDataFrame to specified path in GeoJSON form.

    Arguments:
        counties {GeoDataFrame} -- Counties GeoDataFrame
        path {str} -- Path to export GeoJSON to
    """
    counties.to_file(path, driver="GeoJSON")


def main():
    """Load counties from GIS shape zip, add ACH regions, dissolve by ACH region, and export to GeoJSON.
    """
    counties = load_counties()
    counties = add_regions(counties)
    dissolved = dissolve_counties(counties)
    export_geojson(dissolved, BASE_DIR / "dissolved.geojson")


if __name__ == "__main__":
    main()
