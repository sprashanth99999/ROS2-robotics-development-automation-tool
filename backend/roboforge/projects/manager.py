"""Project manager — CRUD for ROS2 workspaces."""

from __future__ import annotations

import json
import shutil
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from datetime import datetime

from roboforge.config.paths import projects_dir
from roboforge.utils.logging import get_logger

log = get_logger(__name__)


@dataclass
class Project:
    id: str = ""
    name: str = ""
    template: str = "empty"
    ros2_distro: str = "humble"
    workspace_path: str = ""
    urdf_path: str = ""
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def _meta_path(project_path: Path) -> Path:
    return project_path / ".roboforge" / "project.json"


def list_projects() -> list[Project]:
    """List all projects in projects dir."""
    base = Path(projects_dir())
    projects = []
    if not base.exists():
        return projects
    for d in sorted(base.iterdir()):
        meta = _meta_path(d)
        if meta.exists():
            data = json.loads(meta.read_text())
            projects.append(Project(**data))
    return projects


def get_project(project_id: str) -> Project | None:
    for p in list_projects():
        if p.id == project_id:
            return p
    return None


def create_project(name: str, template: str = "empty", ros2_distro: str = "humble") -> Project:
    """Create new project with workspace scaffold."""
    pid = uuid.uuid4().hex[:8]
    now = datetime.utcnow().isoformat()
    ws_path = Path(projects_dir()) / f"{name}_{pid}"
    ws_path.mkdir(parents=True, exist_ok=True)

    project = Project(
        id=pid, name=name, template=template,
        ros2_distro=ros2_distro, workspace_path=str(ws_path),
        created_at=now, updated_at=now,
    )

    # Scaffold workspace
    (ws_path / "src").mkdir(exist_ok=True)
    (ws_path / ".roboforge").mkdir(exist_ok=True)
    _meta_path(ws_path).write_text(json.dumps(project.to_dict(), indent=2))

    # Apply template
    _apply_template(ws_path, template, name, ros2_distro)

    log.info("Created project %s at %s", name, ws_path)
    return project


def delete_project(project_id: str) -> bool:
    p = get_project(project_id)
    if not p:
        return False
    ws = Path(p.workspace_path)
    if ws.exists():
        shutil.rmtree(ws)
    return True


def update_project(project_id: str, **kwargs) -> Project | None:
    p = get_project(project_id)
    if not p:
        return None
    for k, v in kwargs.items():
        if hasattr(p, k):
            setattr(p, k, v)
    p.updated_at = datetime.utcnow().isoformat()
    meta = _meta_path(Path(p.workspace_path))
    meta.write_text(json.dumps(p.to_dict(), indent=2))
    return p


def _apply_template(ws_path: Path, template: str, name: str, distro: str):
    """Scaffold template files in workspace."""
    src = ws_path / "src"

    if template == "empty":
        return

    if template == "publisher_subscriber":
        pkg = src / name
        pkg.mkdir(exist_ok=True)
        (pkg / "__init__.py").touch()
        (pkg / "publisher.py").write_text(f'''import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Publisher(Node):
    def __init__(self):
        super().__init__("{name}_publisher")
        self.pub = self.create_publisher(String, "topic", 10)
        self.timer = self.create_timer(1.0, self.callback)
    def callback(self):
        msg = String()
        msg.data = "hello from {name}"
        self.pub.publish(msg)

def main():
    rclpy.init()
    rclpy.spin(Publisher())
''')
        (pkg / "subscriber.py").write_text(f'''import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Subscriber(Node):
    def __init__(self):
        super().__init__("{name}_subscriber")
        self.sub = self.create_subscription(String, "topic", self.callback, 10)
    def callback(self, msg):
        self.get_logger().info(f"Received: {{msg.data}}")

def main():
    rclpy.init()
    rclpy.spin(Subscriber())
''')
        (pkg / "package.xml").write_text(f'''<?xml version="1.0"?>
<package format="3">
  <name>{name}</name>
  <version>0.0.1</version>
  <description>{name} package</description>
  <maintainer email="dev@roboforge.ai">dev</maintainer>
  <license>MIT</license>
  <depend>rclpy</depend>
  <depend>std_msgs</depend>
  <export><build_type>ament_python</build_type></export>
</package>
''')
        (pkg / "setup.py").write_text(f'''from setuptools import setup
setup(
    name="{name}",
    version="0.0.1",
    packages=["{name}"],
    entry_points={{"console_scripts": [
        "publisher = {name}.publisher:main",
        "subscriber = {name}.subscriber:main",
    ]}},
)
''')

    elif template == "service":
        pkg = src / name
        pkg.mkdir(exist_ok=True)
        (pkg / "__init__.py").touch()
        (pkg / "server.py").write_text(f'''import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts

class Server(Node):
    def __init__(self):
        super().__init__("{name}_server")
        self.srv = self.create_service(AddTwoInts, "add_two_ints", self.callback)
    def callback(self, req, resp):
        resp.sum = req.a + req.b
        return resp

def main():
    rclpy.init()
    rclpy.spin(Server())
''')
