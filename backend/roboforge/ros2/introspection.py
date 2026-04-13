"""ROS2 runtime introspection — nodes, topics, services via CLI."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field

from roboforge.utils.logging import get_logger

log = get_logger(__name__)


@dataclass
class TopicInfo:
    name: str
    msg_type: str
    publishers: list[str] = field(default_factory=list)
    subscribers: list[str] = field(default_factory=list)
    hz: float | None = None


@dataclass
class NodeInfo:
    name: str
    namespace: str = "/"
    publishers: list[str] = field(default_factory=list)
    subscribers: list[str] = field(default_factory=list)
    services: list[str] = field(default_factory=list)


async def _run(cmd: str) -> str:
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
        return stdout.decode(errors="replace").strip()
    except Exception as e:
        log.warning("introspection cmd failed: %s → %s", cmd, e)
        return ""


async def list_nodes() -> list[str]:
    out = await _run("ros2 node list")
    return [n for n in out.splitlines() if n.startswith("/")]


async def list_topics() -> list[TopicInfo]:
    out = await _run("ros2 topic list -t")
    topics = []
    for line in out.splitlines():
        parts = line.strip().split()
        if len(parts) >= 2:
            name = parts[0]
            msg_type = parts[1].strip("[]")
            topics.append(TopicInfo(name=name, msg_type=msg_type))
    return topics


async def get_node_info(node_name: str) -> NodeInfo:
    out = await _run(f"ros2 node info {node_name}")
    info = NodeInfo(name=node_name)
    section = ""
    for line in out.splitlines():
        stripped = line.strip()
        if "Publishers:" in stripped:
            section = "pub"
        elif "Subscribers:" in stripped:
            section = "sub"
        elif "Service Servers:" in stripped or "Service Clients:" in stripped:
            section = "srv"
        elif stripped.startswith("/"):
            topic = stripped.split(":")[0].strip()
            if section == "pub":
                info.publishers.append(topic)
            elif section == "sub":
                info.subscribers.append(topic)
            elif section == "srv":
                info.services.append(topic)
    return info


async def get_topic_info(topic_name: str) -> TopicInfo:
    out = await _run(f"ros2 topic info {topic_name} -v")
    info = TopicInfo(name=topic_name, msg_type="")
    section = ""
    for line in out.splitlines():
        stripped = line.strip()
        if "Type:" in stripped:
            info.msg_type = stripped.split(":", 1)[1].strip()
        elif "Publisher count:" in stripped:
            section = "pub"
        elif "Subscription count:" in stripped:
            section = "sub"
        elif "Node name:" in stripped:
            node = stripped.split(":", 1)[1].strip()
            if section == "pub":
                info.publishers.append(node)
            elif section == "sub":
                info.subscribers.append(node)
    return info


async def list_services() -> list[str]:
    out = await _run("ros2 service list")
    return [s for s in out.splitlines() if s.startswith("/")]


async def snapshot() -> dict:
    """Full snapshot: all nodes + topics + their connections."""
    nodes = await list_nodes()
    topics = await list_topics()

    node_infos = []
    for n in nodes[:50]:  # cap to avoid timeout
        ni = await get_node_info(n)
        node_infos.append(ni)

    return {
        "nodes": [{"name": n.name, "namespace": n.namespace,
                    "publishers": n.publishers, "subscribers": n.subscribers,
                    "services": n.services} for n in node_infos],
        "topics": [{"name": t.name, "msg_type": t.msg_type,
                     "publishers": t.publishers, "subscribers": t.subscribers}
                    for t in topics],
        "timestamp": __import__("time").time(),
    }
