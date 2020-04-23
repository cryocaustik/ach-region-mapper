# ACH Region Mapper

Map US counties to Accountable Communities of Health (ACH) regions as defined by the Health Care Authority in Washington State.

Using GeoPandas, we load GIS Shape files (used in Zip form), map counties to relevant region, and export the results as a GeoJSON file.

## Python Dependencies

- [Python >= 3.8](https://www.python.org/)
- [GeoPandas](https://geopandas.org/)

## Geo Source Files

These files can be replaced with other US County mappings as long as they're kept in similar form.

- [WA County Boundaries shape files](http://data-wadnr.opendata.arcgis.com/datasets/wa-county-boundaries)
- [WA County to ACH Region map](./data/regions.json)

