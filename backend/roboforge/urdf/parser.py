"""URDF parser — extract links, joints, materials from URDF XML."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class UrdfLink:
    name: str
    visual_mesh: str | None = None
    collision_mesh: str | None = None
    material: str | None = None
    origin: dict | None = None


@dataclass
class UrdfJoint:
    name: str
    type: str  # revolute, prismatic, fixed, continuous, floating, planar
    parent: str
    child: str
    axis: list[float] = field(default_factory=lambda: [0, 0, 1])
    lower: float = 0.0
    upper: float = 0.0
    origin: dict | None = None


@dataclass
class UrdfModel:
    name: str = ""
    links: list[UrdfLink] = field(default_factory=list)
    joints: list[UrdfJoint] = field(default_factory=list)
    error: str | None = None

    @property
    def joint_names(self) -> list[str]:
        return [j.name for j in self.joints if j.type != "fixed"]

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "links": [{"name": l.name, "visual_mesh": l.visual_mesh,
                        "material": l.material} for l in self.links],
            "joints": [{"name": j.name, "type": j.type, "parent": j.parent,
                         "child": j.child, "axis": j.axis,
                         "lower": j.lower, "upper": j.upper} for j in self.joints],
        }


def _parse_origin(elem: ET.Element | None) -> dict | None:
    if elem is None:
        return None
    xyz = elem.get("xyz", "0 0 0").split()
    rpy = elem.get("rpy", "0 0 0").split()
    return {"xyz": [float(v) for v in xyz], "rpy": [float(v) for v in rpy]}


def parse_urdf(source: str | Path) -> UrdfModel:
    """Parse URDF from file path or XML string."""
    model = UrdfModel()
    try:
        if Path(str(source)).exists():
            tree = ET.parse(str(source))
            root = tree.getroot()
        else:
            root = ET.fromstring(str(source))
    except Exception as e:
        model.error = f"Parse error: {e}"
        return model

    model.name = root.get("name", "unnamed")

    for link_el in root.findall("link"):
        link = UrdfLink(name=link_el.get("name", ""))
        visual = link_el.find("visual")
        if visual is not None:
            mesh = visual.find(".//mesh")
            if mesh is not None:
                link.visual_mesh = mesh.get("filename")
            mat = visual.find("material")
            if mat is not None:
                link.material = mat.get("name")
            link.origin = _parse_origin(visual.find("origin"))
        collision = link_el.find("collision")
        if collision is not None:
            mesh = collision.find(".//mesh")
            if mesh is not None:
                link.collision_mesh = mesh.get("filename")
        model.links.append(link)

    for joint_el in root.findall("joint"):
        parent = joint_el.find("parent")
        child = joint_el.find("child")
        joint = UrdfJoint(
            name=joint_el.get("name", ""),
            type=joint_el.get("type", "fixed"),
            parent=parent.get("link", "") if parent is not None else "",
            child=child.get("link", "") if child is not None else "",
        )
        axis_el = joint_el.find("axis")
        if axis_el is not None:
            joint.axis = [float(v) for v in axis_el.get("xyz", "0 0 1").split()]
        limit_el = joint_el.find("limit")
        if limit_el is not None:
            joint.lower = float(limit_el.get("lower", 0))
            joint.upper = float(limit_el.get("upper", 0))
        joint.origin = _parse_origin(joint_el.find("origin"))
        model.joints.append(joint)

    return model
