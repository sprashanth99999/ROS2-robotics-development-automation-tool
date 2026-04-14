"""RoboForge CLI entrypoint."""

from __future__ import annotations

import argparse
import sys


def cli():
    parser = argparse.ArgumentParser(description="RoboForge AI CLI")
    sub = parser.add_subparsers(dest="command")

    # Server
    srv = sub.add_parser("serve", help="Start backend server")
    srv.add_argument("--port", type=int, default=0)
    srv.add_argument("--host", type=str, default=None)

    # Project
    proj = sub.add_parser("project", help="Project management")
    proj_sub = proj.add_subparsers(dest="action")
    proj_sub.add_parser("list", help="List projects")
    cr = proj_sub.add_parser("create", help="Create project")
    cr.add_argument("name")
    cr.add_argument("--template", default="empty")
    cr.add_argument("--distro", default="humble")
    dl = proj_sub.add_parser("delete", help="Delete project")
    dl.add_argument("id")

    # ROS2
    ros = sub.add_parser("ros2", help="ROS2 operations")
    ros_sub = ros.add_subparsers(dest="action")
    ros_sub.add_parser("detect", help="Detect ROS2 installation")
    ros_sub.add_parser("install", help="Install ROS2")

    # RAG
    rag = sub.add_parser("index", help="Index files for RAG")
    rag.add_argument("path")

    args = parser.parse_args()

    if args.command == "serve":
        from roboforge.server import run
        sys.argv = ["roboforge"]
        if args.port:
            sys.argv.extend(["--port", str(args.port)])
        if args.host:
            sys.argv.extend(["--host", args.host])
        run()

    elif args.command == "project":
        from roboforge.projects.manager import list_projects, create_project, delete_project
        if args.action == "list":
            for p in list_projects():
                print(f"  {p.id}  {p.name}  {p.template}  {p.workspace_path}")
        elif args.action == "create":
            p = create_project(args.name, args.template, args.distro)
            print(f"Created: {p.name} ({p.id}) at {p.workspace_path}")
        elif args.action == "delete":
            ok = delete_project(args.id)
            print("Deleted" if ok else "Not found")

    elif args.command == "ros2":
        from roboforge.ros2.detector import detect_ros2
        if args.action == "detect":
            d = detect_ros2()
            print(d.summary)

    elif args.command == "index":
        from roboforge.rag.indexer import RagIndexer
        idx = RagIndexer()
        idx.init_table()
        count = idx.index_directory(args.path)
        print(f"Indexed {count} chunks from {args.path}")

    else:
        parser.print_help()


if __name__ == "__main__":
    cli()
