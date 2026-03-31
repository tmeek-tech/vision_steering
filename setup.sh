#!/bin/bash
set -e

# ── Locale ────────────────────────────────────────────────────────────────────
sudo apt update && sudo apt install -y locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# ── ROS 2 Humble repo ─────────────────────────────────────────────────────────
sudo apt install -y software-properties-common curl
sudo add-apt-repository universe -y

export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest \
  | grep -F "tag_name" | awk -F'"' '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb \
  "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb

# ── ROS 2 Humble install ───────────────────────────────────────────────────────
sudo apt update && sudo apt upgrade -y
sudo apt install -y ros-humble-desktop
sudo apt install -y ros-humble-ros-gz

# ── TurtleBot3 dependencies ───────────────────────────────────────────────────
sudo apt install -y ros-humble-gazebo-*
sudo apt install -y \
  ros-humble-cartographer \
  ros-humble-cartographer-ros \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup

sudo apt install -y python3-colcon-common-extensions

# ── TurtleBot3 workspace ───────────────────────────────────────────────────────
source /opt/ros/humble/setup.bash

mkdir -p ~/turtlebot3_ws/src
cd ~/turtlebot3_ws/src
git clone -b humble https://github.com/ROBOTIS-GIT/DynamixelSDK.git
git clone -b humble https://github.com/ROBOTIS-GIT/turtlebot3_msgs.git
git clone -b humble https://github.com/ROBOTIS-GIT/turtlebot3.git
git clone -b humble https://github.com/ROBOTIS-GIT/turtlebot3_simulations.git

# ── Vision steering package ───────────────────────────────────────────────────
git clone https://github.com/tmeek-tech/vision_steering.git

cd ~/turtlebot3_ws
colcon build --symlink-install
colcon build --symlink-install --packages-select vision_steering

# ── Persist environment to ~/.bashrc ─────────────────────────────────────────
cat >> ~/.bashrc << 'EOF'
source /opt/ros/humble/setup.bash
source /usr/share/gazebo/setup.sh
source ~/turtlebot3_ws/install/setup.bash
export ROS_DOMAIN_ID=30
export TURTLEBOT3_MODEL=burger
EOF

source ~/.bashrc

echo ""
echo "✅ Installation complete! Open a new terminal or run: source ~/.bashrc"
