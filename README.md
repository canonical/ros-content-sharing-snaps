# ros-content-sharing-snaps
ROS content sharing snaps generator

This repository contains various scripts to generate the content sharing snaps for ROS.
The snapcraft extensions corresponding to these content-sharing can be found the snapcraft documentation for [ROS](https://snapcraft.io/docs/ros-noetic-content-extension) and [ROS 2](https://snapcraft.io/docs/ros2-jazzy-content-extension).

Additionaly, this repository contains the CI to build and upload the content sharing snaps.

## Scripts

### generate_package_xml_recursive_dependencies

Generate a `package.xml` with all the recursive `build`, `buildtool`, `build_export`, `buildtool_export`, `exec`, `run` and `test` dependencies as exec depends.

```
optional arguments:
  -h, --help            show this help message and exit
  --rosdistro {noetic,foxy,humble,jazzy}
                        The ROS distro to evaluate.
  --variant {desktop,desktop-full,perception,robot,ros-base,ros-core}
                        The ROS (install) metapackage to serve as a variant. (default: None).
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        package.xml file to write for dependencies
  -c CMAKE_FILE, --cmake-file CMAKE_FILE
                        CMakeLists.txt file to write for metapackages
```
### generate_ros_meta_snapcraft_file

Generate a `snapcraft.yaml` file for a ROS foundational snap.

```
optional arguments:
  -h, --help            show this help message and exit
  -r {noetic,foxy,humble,jazzy}, --rosdistro {noetic,foxy,humble,jazzy}
                        The ROS distro to target.
  -v {desktop,desktop-full,perception,robot,ros-base,ros-core}, --variant {desktop,desktop-full,perception,robot,ros-base,ros-core}
                        The ROS metapackage to serve as a baseline. (default: ros-core).
  -p PATH, --path PATH  Output path for generated files.
  -s, --snap            Run snapcraft.
  -d, --dev             Generate the dev snap.
  -q, --quiet           Do not print.
```

### generate_all_ros_meta_snapcraft_file

Generate a `snapcraft.yaml`` file for all ROS foundational snap.

```
optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Output path for generated files.
  -s, --snap            Run snapcraft for the generated files.
```