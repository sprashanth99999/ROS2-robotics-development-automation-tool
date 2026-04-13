import { useEffect } from "react";
import { useRos2Store } from "../../state/ros2Store";
import { useRos2Graph } from "../../features/ros2/useRos2Graph";

export function TopicMonitor() {
  const { topics, loading } = useRos2Store();
  const { fetchTopics } = useRos2Graph();

  useEffect(() => {
    fetchTopics();
    const iv = setInterval(fetchTopics, 3000);
    return () => clearInterval(iv);
  }, [fetchTopics]);

  return (
    <div style={{ padding: 16 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
        <b style={{ color: "#58a6ff", fontSize: 14 }}>Topics</b>
        <span style={{ color: "#8b949e", fontSize: 11 }}>
          {loading ? "updating..." : `${topics.length} topics`}
        </span>
      </div>
      {topics.length === 0 ? (
        <div style={{ color: "#8b949e", fontSize: 13 }}>
          No topics detected. Start ROS2 nodes to see topics.
        </div>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
          <thead>
            <tr style={{ borderBottom: "1px solid #21262d" }}>
              <th style={{ textAlign: "left", padding: "6px 8px", color: "#8b949e" }}>Topic</th>
              <th style={{ textAlign: "left", padding: "6px 8px", color: "#8b949e" }}>Type</th>
            </tr>
          </thead>
          <tbody>
            {topics.map((t) => (
              <tr key={t.name} style={{ borderBottom: "1px solid #161b22" }}>
                <td style={{ padding: "6px 8px", color: "#3fb950", fontFamily: "monospace" }}>
                  {t.name}
                </td>
                <td style={{ padding: "6px 8px", color: "#c9d1d9" }}>{t.msg_type}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
