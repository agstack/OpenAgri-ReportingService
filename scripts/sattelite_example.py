import io
import requests
from fastapi import HTTPException
# --- Service Definition ---
# EOX Sentinel-2 Cloudless (Global, Commercial Use OK, CC BY 4.0)
# This uses the 2016 layer, which is licensed for commercial use.
EOX_WMS_URL = "https://tiles.maps.eox.at/wms"
EOX_LAYER = "s2cloudless"


def fetch_wms_image(
        lat: float,
        lon: float,
        wms_url: str = EOX_WMS_URL,
        layer_name: str = EOX_LAYER,
        size_degrees: float = 1.8,
        width: int = 1600,
        height: int = 1200
):
    """
    Fetches an image from a standard WMS service.
    """

    half_size = size_degrees / 200.0
    min_lat = lat - half_size
    max_lat = lat + half_size
    min_lon = lon - half_size
    max_lon = lon + half_size

    bbox_1_3_0 = f"{min_lat},{min_lon},{max_lat},{max_lon}"
    crs_1_3_0 = "EPSG:4326"

    #Define the WMS parameters
    wms_params = {
        'SERVICE': 'WMS',
        'REQUEST': 'GetMap',
        'VERSION': '1.3.0',
        'LAYERS': layer_name,
        'STYLES': '',
        'FORMAT': 'image/png',
        'TRANSPARENT': 'true',
        'CRS': crs_1_3_0,
        'BBOX': bbox_1_3_0,
        'WIDTH': width,
        'HEIGHT': height
    }

    try:
        response = requests.get(wms_url, params=wms_params, timeout=20)
        response.raise_for_status()

        if 'image' not in response.headers.get('Content-Type', ''):
            raise HTTPException(
                status_code=404,
                detail=f"No imagery found or error from WMS: {response.text}"
            )

        return response.content

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Error fetching image from WMS: {e}")


image_bytes = fetch_wms_image(45.243248, 19.837172 )
image_file = io.BytesIO(image_bytes)
# Write the stuff
with open("../output.png", "wb") as f:
    f.write(image_file.getbuffer())
