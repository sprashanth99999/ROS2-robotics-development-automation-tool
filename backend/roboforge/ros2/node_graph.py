"""Node graph builder — transforms introspection data into graph format."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from roboforge.ros2.introspection import snapshot
from roboforge.utils.logging import get_logger

log = get_logger(__name__)


@dataclass
class GraphNode:
    id: str
    label: str
    type: str  # "node" | "topic"
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
    source: str
    target: str
    label: str = ""
    type: str = "publishes"  # "publishes" | "subscribes"


@dataclass
class NodeGraph:
    nodes: list[GraphNode] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)
    timestamp: float = 0.0

    def to_dict(self) -> dict:
        return {
            "nodes": [{"id": n.id, "label": n.label, "type": n.type, "data": n.data}
                       for n in self.nodes],
            "edges": [{"source": e.source, "target": e.target, "label": e.label, "type": e.type}
                       for e in self.edges],
            "timestamp": self.timestamp,
        }


async def build_graph() -> NodeGraph:
    """Build node graph from live ROS2 introspection."""
    snap = await snapshot()
    graph = NodeGraph(timestamp=snap["timestamp"])

    seen_ids: set[str] = set()

    # Add ROS2 nodes
    for n in snap["nodes"]:
        nid = f"node:{n['name']}"
        if nid not in seen_ids:
            graph.nodes.append(GraphNode(id=nid, label=n["name"], type="node",
                                          data={"services": n.get("services", [])}))
            seen_ids.add(nid)

        # Edges: node → topic (publishes)
        for pub in n.get("publishers", []):
            tid = f"topic:{pub}"
            if tid not in seen_ids:
                graph.nodes.append(GraphNode(id=tid, label=pub, type="topic"))
                seen_ids.add(tid)
            graph.edges.append(GraphEdge(source=nid, target=tid, type="publishes"))

        # Edges: topic → node (subscribes)
        for sub in n.get("subscribers", []):
            tid = f"topic:{sub}"
            if tid not in seen_ids:
                graph.nodes.append(GraphNode(id=tid, label=sub, type="topic"))
                seen_ids.add(tid)
            graph.edges.append(GraphEdge(source=tid, target=nid, type="subscribes"))

    # Add any topics from topic list not already captured
    for t in snap["topics"]:
        tid = f"topic:{t['name']}"
        if tid not in seen_ids:
            graph.nodes.append(GraphNode(id=tid, label=t["name"], type="topic",
                                          data={"msg_type": t["msg_type"]}))
            seen_ids.add(tid)

    log.info("Built graph: %d nodes, %d edges", len(graph.nodes), len(graph.edges))
    return graph


def build_graph_from_snapshot(snap: dict) -> NodeGraph:
    """Build graph from pre-fetched snapshot (no async)."""
    graph = NodeGraph(timestamp=snap.get("timestamp", 0))
    seen: set[str] = set()

    for n in snap.get("nodes", []):
        nid = f"node:{n['name']}"
        if nid not in seen:
            graph.nodes.append(GraphNode(id=nid, label=n["name"], type="node"))
            seen.add(nid)
        for pub in n.get("publishers", []):
            tid = f"topic:{pub}"
            if tid not in seen:
                graph.nodes.append(GraphNode(id=tid, label=pub, type="topic"))
                seen.add(tid)
            graph.edges.append(GraphEdge(source=nid, target=tid, type="publishes"))
        for sub in n.get("subscribers", []):
            tid = f"topic:{sub}"
            if tid not in seen:
                graph.nodes.append(GraphNode(id=tid, label=sub, type="topic"))
                seen.add(tid)
            graph.edges.append(GraphEdge(source=tid, target=nid, type="subscribes"))

    return graph
