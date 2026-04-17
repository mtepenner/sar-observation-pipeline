import React, { useState } from "react";
import DeckGLMap from "./components/DeckGLMap";
import TimeSlider from "./components/TimeSlider";
import AnalysisSidebar from "./components/AnalysisSidebar";
import { useVectorData } from "./hooks/useVectorData";

const MIN_DATE = "2020-01-01";
const MAX_DATE = new Date().toISOString().split("T")[0];

const DEFAULT_VIEWPORT = {
  longitude: 0,
  latitude: 20,
  zoom: 3,
};

/**
 * Root application component.
 *
 * Composes the DeckGL map canvas, the time-scrubber, and the analysis
 * sidebar into a full-screen SAR visualisation dashboard.
 */
const App: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState<string>(MAX_DATE);
  const { loading, featureCount } = useVectorData(DEFAULT_VIEWPORT, selectedDate);

  const metrics = [
    { label: "Change Events", value: loading ? "…" : String(featureCount) },
    { label: "Selected Date", value: selectedDate },
  ];

  return (
    <div style={{ width: "100vw", height: "100vh", position: "relative", background: "#111" }}>
      <DeckGLMap selectedDate={selectedDate} />
      <TimeSlider
        minDate={MIN_DATE}
        maxDate={MAX_DATE}
        value={selectedDate}
        onChange={setSelectedDate}
      />
      <AnalysisSidebar
        selectedDate={selectedDate}
        metrics={metrics}
        loading={loading}
      />
    </div>
  );
};

export default App;
