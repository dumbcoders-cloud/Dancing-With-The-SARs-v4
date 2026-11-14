"""PyDeck layer construction for NASA imagery and synthetic study-area scenes."""

from __future__ import annotations

from datetime import date
import math
from typing import Any

import pydeck as pdk


def _footprint(study: Any) -> dict[str, Any]:
    half_lon = study.grid_lon_step * 4.8
    half_lat = study.grid_lat_step * 3.8
    west, east = study.longitude - half_lon, study.longitude + half_lon
    south, north = study.latitude - half_lat, study.latitude + half_lat
    return {
        "type": "Feature",
        "properties": {"name": f"Synthetic footprint · {study.name}"},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[west, south], [east, south], [east, north], [west, north], [west, south]]],
        },
    }


def _latitude_for_tile_row(row: int, zoom: int) -> float:
    """Return the north/south edge of a GoogleMapsCompatible Web Mercator tile."""
    scale = 2**zoom
    return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * row / scale))))


def _nasa_imagery_layers(study: Any, observation_date: date) -> list[pdk.Layer]:
    """Build a small image-tile neighborhood without PyDeck's unsupported JS callback.

    PyDeck's standalone JSON converter treats string props as simple expressions; it
    cannot compile a custom ``renderSubLayers`` arrow function. Emitting regular
    BitmapLayers keeps the GIBS WMTS tiles declarative and works in WebView2.
    """
    zoom = min(9, max(0, math.floor(study.zoom)))
    if abs(study.latitude) >= 66.5:
        polar_winter = (
            study.latitude >= 0 and observation_date.month in {11, 12, 1, 2}
        ) or (study.latitude < 0 and observation_date.month in {5, 6, 7, 8})
        if polar_winter:
            # The true-color product is effectively black during polar night;
            # keep the CARTO reference map and simulated overlays visible.
            return []

    tile_count = 2**zoom
    center_x = math.floor((study.longitude + 180) / 360 * tile_count)
    latitude_radians = math.radians(study.latitude)
    center_y = math.floor(
        (1 - math.asinh(math.tan(latitude_radians)) / math.pi) / 2 * tile_count
    )
    date_text = observation_date.isoformat()
    layers: list[pdk.Layer] = []

    # Five columns by three rows cover the study scene and a useful context margin
    # at all four configured zoom levels, while keeping a timeline update light.
    for tile_x in range(center_x - 2, center_x + 3):
        if not 0 <= tile_x < tile_count:
            continue
        west = tile_x / tile_count * 360 - 180
        east = (tile_x + 1) / tile_count * 360 - 180
        for tile_y in range(center_y - 1, center_y + 2):
            if not 0 <= tile_y < tile_count:
                continue
            north = _latitude_for_tile_row(tile_y, zoom)
            south = _latitude_for_tile_row(tile_y + 1, zoom)
            tile_url = (
                "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/"
                "MODIS_Terra_CorrectedReflectance_TrueColor/default/"
                f"{date_text}/GoogleMapsCompatible_Level9/{zoom}/{tile_y}/{tile_x}.jpg"
            )
            layers.append(
                pdk.Layer(
                    "BitmapLayer",
                    id=f"nasa-modis-terra-{date_text}-{zoom}-{tile_x}-{tile_y}",
                    # Quoted strings are serialized as literal URLs by PyDeck.
                    image=f'"{tile_url}"',
                    bounds=[west, south, east, north],
                    opacity=0.68,
                    pickable=False,
                )
            )
    return layers


def build_deck(
    records: list[dict[str, Any]],
    study: Any,
    show_vectors: bool,
    show_footprint: bool,
    map_style: str = "dark",
    observation_date: date | None = None,
    show_nasa_imagery: bool = True,
) -> pdk.Deck:
    layers: list[pdk.Layer] = []

    if show_nasa_imagery and observation_date is not None:
        layers.extend(_nasa_imagery_layers(study, observation_date))

    if show_footprint:
        layers.append(
            pdk.Layer(
                "GeoJsonLayer",
                data=_footprint(study),
                stroked=True,
                filled=True,
                get_fill_color=[57, 204, 201, 18],
                get_line_color=[91, 220, 211, 180],
                get_line_width=2,
                line_width_min_pixels=1,
                pickable=True,
            )
        )

    if show_vectors:
        layers.append(
            pdk.Layer(
                "PathLayer",
                data=records,
                get_path="path",
                get_color=[245, 174, 104, 145],
                get_width=2,
                width_min_pixels=1,
                width_units="pixels",
                pickable=True,
            )
        )

    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=records,
            get_position="[lon, lat]",
            get_fill_color="color",
            get_radius="radius_m",
            radius_units="meters",
            radius_min_pixels=4,
            radius_max_pixels=13,
            line_width_min_pixels=1,
            stroked=True,
            get_line_color=[10, 20, 28, 220],
            pickable=True,
            auto_highlight=True,
        )
    )

    return pdk.Deck(
        layers=layers,
        initial_view_state=pdk.ViewState(
            latitude=study.latitude,
            longitude=study.longitude,
            zoom=study.zoom,
            pitch=18,
            bearing=-8,
        ),
        map_provider="carto",
        map_style=map_style,
        tooltip={
            "html": "<b>{sample_id}</b><br/>Velocity: {velocity_label}<br/>Displacement: {displacement_label}",
            "style": {"backgroundColor": "#101b24", "color": "#e6f1f5", "fontSize": "12px"},
        },
    )
