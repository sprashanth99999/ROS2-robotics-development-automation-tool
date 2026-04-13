import { useEffect, useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  type Node,
  type Edge,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useRos2Store } from "../../state/ros2Store";
import { useRos2Graph } from "../../features/ros2/useRos2Graph";

const NODE_COLORS: Record<string, string> = {
  node: "#238636",
  topic: "#58a6ff",
};

export function NodeGraph() {
  const { nodes: gNodes, edges: gEdges, loading } = useRos2Store();
  const { refresh } = useRos2Graph();

  useEffect(() => {
    refresh();
    const iv = setInterval(refresh, 5000);
    return () => clearInterval(iv);
  }, [refresh]);

  const rfNodes: Node[] = useMemo(
    () =>
      gNodes.map((n, i) => ({
        id: n.id,
        position: {
          x: n.type === "node" ? 50 : 350,
          y: i * 80,
        },
        data: { label: n.label },
        style: {
          background: NODE_COLORS[n.type] || "#21262d",
          color: "#fff",
          border: "1px solid #30363d",
          borderRadius: 8,
          padding: "8px 12px",
          fontSize: 12,
          fontFamily: "monospace",
        },
      })),
    [gNodes]
  );

  const rfEdges: Edge[] = useMemo(
    () =>
      gEdges.map((e, i) => ({
        id: `e-${i}`,
        source: e.source,
        target: e.target,
        animated: e.type === "publishes",
        style: { stroke: e.type === "publishes" ? "#3fb950" : "#58a6ff" },
      })),
    [gEdges]
  );

  if (loading && gNodes.length === 0) {
    return (
      <div style={{ padding: 32, color: "#8b949e", textAlign: "center" }}>
        Loading ROS2 graph...
      </div>
    );
  }

  if (gNodes.length === 0) {
    return (
      <div style={{ padding: 32, color: "#8b949e", textAlign: "center" }}>
        No ROS2 nodes detected. Start a ROS2 system to see the graph.
        <br />
        <button
          onClick={refresh}
          style={{ marginTop: 12, background: "#21262d", color: "#c9d1d9", border: "1px solid #30363d", borderRadius: 6, padding: "6px 16px", cursor: "pointer" }}
        >
          Refresh
        </button>
      </div>
    );
  }

  return (
    <div style={{ width: "100%", height: "100%" }}>
      <ReactFlow
        nodes={rfNodes}
        edges={rfEdges}
        fitView
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#21262d" gap={20} />
        <Controls />
        <MiniMap
          style={{ background: "#0d1117" }}
          nodeColor={(n) => NODE_COLORS[n.type as string] || "#21262d"}
        />
      </ReactFlow>
    </div>
  );
}
