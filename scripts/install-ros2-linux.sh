#!/usr/bin/env bash
# RoboForge AI — ROS2 Humble installer for Ubuntu 22.04/24.04
# Usage: bash install-ros2-linux.sh [--distro humble|jazzy] [--dry-run]
set -euo pipefail

DISTRO="${1:-humble}"
DRY_RUN=false
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --distro) shift; DISTRO="$1" ;;
  esac
done

log() { echo "[roboforge] $*"; }
run() {
  log ">> $*"
  if [ "$DRY_RUN" = true ]; then
    log "(dry-run) skipped"
  else
    eval "$@"
  fi
}

# Pre-checks
if [ -f "/opt/ros/$DISTRO/setup.bash" ]; then
  log "ROS2 $DISTRO already installed at /opt/ros/$DISTRO"
  exit 0
fi

if ! grep -q "Ubuntu" /etc/os-release 2>/dev/null; then
  log "ERROR: Ubuntu required. Detected: $(. /etc/os-release && echo $ID)"
  exit 1
fi

log "Installing ROS2 $DISTRO..."

# 1. Locale
run "sudo locale-gen en_US en_US.UTF-8"
run "sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8"

# 2. Universe repo
run "sudo apt install -y software-properties-common"
run "sudo add-apt-repository universe -y"

# 3. GPG key
run "sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg"

# 4. Apt source
CODENAME=$(. /etc/os-release && echo "$UBUNTU_CODENAME")
run "echo \"deb [arch=\$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $CODENAME main\" | sudo tee /etc/apt/sources.list.d/ros2.list"

# 5. Update + install
run "sudo apt update"
run "sudo apt install -y ros-${DISTRO}-desktop"

# 6. Build tools
run "sudo apt install -y python3-colcon-common-extensions"

# 7. rosdep
run "sudo rosdep init || true"
run "rosdep update"

# 8. Source
if ! grep -q "ros/$DISTRO/setup.bash" ~/.bashrc; then
  run "echo 'source /opt/ros/$DISTRO/setup.bash' >> ~/.bashrc"
fi

log "Done! Run: source ~/.bashrc"
