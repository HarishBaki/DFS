# %%
# =============================================================================
# IMPORT PACKAGES
# =============================================================================
import os
import argparse
from datetime import datetime, timedelta
import numpy as np
import xarray as xr
import zarr
import pystac_client
import planetary_computer

# %%
# =============================================================================
# CONFIGURATION SETTINGS
# =============================================================================
# Output directory for daily NetCDF files
ROOT_DIR = "data/"
OUTPUT_DIR = ROOT_DIR + "CONUS404/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# New York State grid indices
i1 = 1045  # west_east start index
i2 = 1215  # west_east end index  
j1 = 610   # south_north start index
j2 = 740   # south_north end index

ny_indices = {"south_north": slice(j1, j2), "west_east": slice(i1, i2)}

# %%
# ================================================================================
# ARGUMENT PARSER (SPECIFIC DAY)
# ================================================================================
parser = argparse.ArgumentParser(description="Download CONUS404 data for a specific day")
parser.add_argument("--date", type=str, default="1979-10-01", help="Date in YYYY-MM-DD")
args, _ = parser.parse_known_args()   # ✅ ignores Jupyter’s -f flag
target_date = datetime.strptime(args.date, "%Y-%m-%d")

# ================================================================================
# EXECUTION INFORMATION DISPLAY
# ================================================================================
print("=" * 80)
print("CONUS404 NEW YORK STATE 10-METER WIND DATA DOWNLOAD")
print("=" * 80)
print(f"Target Region:      New York State")
print(f"Target Date:        {target_date.strftime('%Y-%m-%d')}")
print(f"Grid Dimensions:    {j2 - j1} x {i2 - i1}  points")
print(f"Total Grid Points:  {(j2 - j1) * (i2 - i1):,}")
print(f"Output Directory:   {OUTPUT_DIR}")
print(f"Variables:          U10, V10, MUCAPE, MLCAPE, SBCAPE, USHR6, VSHR6")
print("=" * 80)

# %%
# ================================================================================
# DATASET CONNECTION AND INITIALIZATION
# ================================================================================
print("Initializing connection to Microsoft Planetary Computer...")

cat = pystac_client.Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace,
)

col = cat.get_collection("conus404")
asset = col.assets["zarr-abfs"]

print("Opening CONUS404 zarr dataset...")

ds_all = xr.open_zarr(
    asset.href,
    storage_options=asset.extra_fields.get("xarray:storage_options", {}),
    **asset.extra_fields.get("xarray:open_kwargs", {}),
)

ds_sub = ds_all[["U10","V10","USHR6","VSHR6","SBCAPE","MLCAPE","MUCAPE"]].isel(**ny_indices)
print("Dataset connection established and subsetted to NY region")

xr.set_options(keep_attrs=True)

# %%
# ================================================================================
# PROCESS SINGLE DAY
# ================================================================================
date_str = target_date.strftime("%Y-%m-%d")
year_dir = os.path.join(OUTPUT_DIR, str(target_date.year))
os.makedirs(year_dir, exist_ok=True)
out_nc = os.path.join(year_dir, f"ny_wind_10m_{date_str}.nc")

print(f"Processing {date_str}...")

try:
    ds_day = ds_sub.sel(time=slice(f"{date_str}T00:00", f"{date_str}T23:00"))
    if ds_day.time.size == 0:
        raise ValueError("No data found for this day")

    wspd = np.hypot(ds_day["U10"], ds_day["V10"]).rename("WIND_SPEED_10M")
    wspd.attrs.update({
        "long_name": "10-meter wind speed",
        "units": "m s-1",
        "description": "Wind speed calculated from U10 and V10 components",
        "formula": "sqrt(U10² + V10²)",
        "standard_name": "wind_speed"
    })

    for v in ("U10", "V10"):
        if "units" not in ds_day[v].attrs:
            ds_day[v].attrs["units"] = "m s-1"

    out = xr.Dataset(
        data_vars={
            "WIND_SPEED_10M": wspd.astype("float32"),
            "U10": ds_day["U10"].astype("float32"),
            "V10": ds_day["V10"].astype("float32"),
            "MUCAPE": ds_day["MUCAPE"].astype("float32"),
            "MLCAPE": ds_day["MLCAPE"].astype("float32"),
            "SBCAPE": ds_day["SBCAPE"].astype("float32"),
            "USHR6": ds_day["USHR6"].astype("float32"),
            "VSHR6": ds_day["VSHR6"].astype("float32"),
        }
    )

    ny_south_north = j2 - j1
    ny_west_east = i2 - i1
    encoding = {
        var: {
            "zlib": True,
            "complevel": 2,
            "dtype": "float32",
            "chunksizes": (ds_day.sizes["time"], min(80, ny_south_north),
                            min(80, ny_west_east))
        }
        for var in out.data_vars
    }

    out.attrs.update({
        "title": f"CONUS404 10m Wind Data - New York State - {date_str}",
        "source": "CONUS404 dataset via Microsoft Planetary Computer",
        "institution": "NCAR/USGS collaboration",
        "model": "Weather Research and Forecasting (WRF) Model v3.9.1.1",
        "grid_bounds": "NY state domain",
        "grid_indices": f"south_north[{j1}:{j2}], west_east[{i1}:{i2}]",
        "spatial_resolution": "4 km",
        "temporal_resolution": "hourly",
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "time_steps": ds_day.time.size,
        "conventions": "CF-1.8"
    })

    out.to_netcdf(out_nc, encoding=encoding)
    print(f"✓ Saved {out_nc} ({ds_day.time.size} hours)")

except Exception as e:
    print(f"✗ Error processing {date_str}: {e}")
# %%
