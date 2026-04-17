import React, { useState } from "react";
import { Map } from "react-map-gl/maplibre";
import DeckGL from "@deck.gl/react";
import { MVTLayer } from "@deck.gl/geo-layers";
import type { PickingInfo } from "@deck.gl/core";

const INITIAL_VIEW_STATE = {
  longitude: 0,
  latitude: 20,
  zoom: 3,
  pitch: 0,
  bearing: 0,
};

interface DeckGLMapProps {
  /** ISO-8601 date string used to filter change tiles by time. */
  selectedDate: string;
  /** Callback fired when a change polygon is clicked. */
  onFeatureClick?: (info: PickingInfo) => void;
}

/**
 * High-performance WebGL map canvas.
 *
 * Renders Mapbox Vector Tiles from the SAR Spatial API using DeckGL's
 * MVTLayer, enabling smooth interaction with millions of change polygons.
 */
const DeckGLMap: React.FC<DeckGLMapProps> = ({ selectedDate, onFeatureClick }) => {
  const [cursor, setCursor] = useState<string>("grab");

  const tilesUrl = `${import.meta.env.VITE_API_URL ?? ""}/tiles/{z}/{x}/{y}.mvt`;

  const changesLayer = new MVTLayer({
    id: "sar-changes",
    data: tilesUrl,
    getFillColor: [255, 80, 0, 160],
    getLineColor: [255, 140, 0, 200],
    lineWidthMinPixels: 1,
    pickable: true,
    autoHighlight: true,
    highlightColor: [255, 255, 0, 200],
    onClick: onFeatureClick,
    onHover: ({ object }) => setCursor(object ? "pointer" : "grab"),
  });

  return (
    <DeckGL
      initialViewState={INITIAL_VIEW_STATE}
      controller
      layers={[changesLayer]}
      getCursor={() => cursor}
      style={{ position: "relative", width: "100%", height: "100%" }}
    >
      <Map
        mapStyle="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
        attributionControl={false}
      />
    </DeckGL>
  );
};

export default DeckGLMap;
