"""URDF validator — checks for common errors."""

from __future__ import annotations

from dataclasses import dataclass, field

from roboforge.urdf.parser import UrdfModel


@dataclass
class ValidationResult:
    valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_urdf(model: UrdfModel) -> ValidationResult:
    """Validate parsed URDF model."""
    result = ValidationResult()

    if model.error:
        result.valid = False
        result.errors.append(model.error)
        return result

    if not model.name:
        result.warnings.append("Robot has no name attribute")

    if not model.links:
        result.valid = False
        result.errors.append("No links defined")
        return result

    # Check all joint parents/children reference existing links
    link_names = {l.name for l in model.links}
    for j in model.joints:
        if j.parent not in link_names:
            result.valid = False
            result.errors.append(f"Joint '{j.name}' references unknown parent link '{j.parent}'")
        if j.child not in link_names:
            result.valid = False
            result.errors.append(f"Joint '{j.name}' references unknown child link '{j.child}'")

    # Check for duplicate names
    seen_links: set[str] = set()
    for l in model.links:
        if l.name in seen_links:
            result.warnings.append(f"Duplicate link name: '{l.name}'")
        seen_links.add(l.name)

    seen_joints: set[str] = set()
    for j in model.joints:
        if j.name in seen_joints:
            result.warnings.append(f"Duplicate joint name: '{j.name}'")
        seen_joints.add(j.name)

    # Check revolute/prismatic joints have limits
    for j in model.joints:
        if j.type in ("revolute", "prismatic") and j.lower == 0 and j.upper == 0:
            result.warnings.append(f"Joint '{j.name}' ({j.type}) has zero limits")

    # Check tree structure (each link except root should be child of exactly one joint)
    children = [j.child for j in model.joints]
    roots = [l.name for l in model.links if l.name not in children]
    if len(roots) == 0:
        result.valid = False
        result.errors.append("No root link found (cyclic structure)")
    elif len(roots) > 1:
        result.warnings.append(f"Multiple root links: {roots}")

    return result
