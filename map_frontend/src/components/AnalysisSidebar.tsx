import React from "react";

interface MetricRow {
  label: string;
  value: string;
}

interface AnalysisSidebarProps {
  /** Date currently selected in the time scrubber (ISO-8601). */
  selectedDate: string;
  /** Computed metrics to display. */
  metrics: MetricRow[];
  /** Whether data is still loading. */
  loading?: boolean;
}

/**
 * Analysis sidebar.
 *
 * Displays computed metrics (e.g. total area of deforestation detected)
 * corresponding to the user's current map viewport and selected date.
 */
const AnalysisSidebar: React.FC<AnalysisSidebarProps> = ({
  selectedDate,
  metrics,
  loading = false,
}) => {
  return (
    <div
      style={{
        position: "absolute",
        top: 20,
        right: 20,
        width: 260,
        background: "rgba(20,20,30,0.9)",
        borderRadius: 8,
        padding: 20,
        color: "#fff",
        zIndex: 10,
      }}
    >
      <h3 style={{ margin: "0 0 8px", fontSize: 14, color: "#ff8040" }}>
        📊 Analysis — {selectedDate}
      </h3>

      {loading ? (
        <p style={{ color: "#aaa", fontSize: 13 }}>Loading…</p>
      ) : metrics.length === 0 ? (
        <p style={{ color: "#aaa", fontSize: 13 }}>No data for selected period.</p>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <tbody>
            {metrics.map(({ label, value }) => (
              <tr key={label} style={{ borderBottom: "1px solid rgba(255,255,255,0.08)" }}>
                <td style={{ padding: "6px 0", color: "#bbb" }}>{label}</td>
                <td style={{ padding: "6px 0", textAlign: "right", fontWeight: 600 }}>
                  {value}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default AnalysisSidebar;
