import React, { useCallback } from "react";

interface TimeSliderProps {
  /** Earliest available date (ISO-8601). */
  minDate: string;
  /** Latest available date (ISO-8601). */
  maxDate: string;
  /** Currently selected date value (ISO-8601). */
  value: string;
  /** Callback fired when the user moves the slider. */
  onChange: (date: string) => void;
}

/**
 * Time scrubber component.
 *
 * Renders an HTML range input mapped to a contiguous date range, allowing
 * the user to scrub through historical SAR change detections.
 */
const TimeSlider: React.FC<TimeSliderProps> = ({ minDate, maxDate, value, onChange }) => {
  const minTs = new Date(minDate).getTime();
  const maxTs = new Date(maxDate).getTime();
  const valueTs = new Date(value).getTime();

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const ts = Number(e.target.value);
      const iso = new Date(ts).toISOString().split("T")[0];
      onChange(iso);
    },
    [onChange],
  );

  return (
    <div
      style={{
        position: "absolute",
        bottom: 32,
        left: "50%",
        transform: "translateX(-50%)",
        background: "rgba(20,20,30,0.85)",
        borderRadius: 8,
        padding: "12px 24px",
        display: "flex",
        alignItems: "center",
        gap: 16,
        zIndex: 10,
      }}
    >
      <span style={{ color: "#aaa", fontSize: 12 }}>{minDate}</span>
      <input
        type="range"
        min={minTs}
        max={maxTs}
        value={valueTs}
        step={86_400_000}
        onChange={handleChange}
        style={{ width: 320, accentColor: "#ff5000" }}
        aria-label="Time scrubber"
      />
      <span style={{ color: "#fff", fontSize: 14, minWidth: 90, textAlign: "center" }}>
        {value}
      </span>
      <span style={{ color: "#aaa", fontSize: 12 }}>{maxDate}</span>
    </div>
  );
};

export default TimeSlider;
