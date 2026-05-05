import argparse
import subprocess
import sys

import rosdistro
from catkin_pkg.package import Dependency
from catkin_pkg.package_templates import (
    PackageTemplate,
    create_cmakelists,
    create_package_xml,
)
from rosdistro.dependency_walker import DependencyWalker


def get_latest_rosdistro_tag(rosdistro_name: str) -> str:
    # removeprefix doesn't exist in python < 3.9
    def remove_prefix(input_string, prefix):
        if prefix and input_string.startswith(prefix):
            return input_string[len(prefix) :]
        return input_string

    result = subprocess.run(
        [
            "git",
            "ls-remote",
            "--tags",
            "--sort=version:refname",
            "https://github.com/ros/rosdistro.git",
            f"refs/tags/{rosdistro_name}/*",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    tags = [
        remove_prefix(line.split("\t")[1], "refs/tags/")
        for line in result.stdout.strip().splitlines()
        if "^{}" not in line
    ]
    if not tags:
        if rosdistro_name == "lyrical":
            print(
                "No lyrical tag found in ros/rosdistro, using master index-v4.yaml "
                "temporarily (lyrical/distribution.yaml)."
            )
            return "master"
        raise RuntimeError(f"No tag found for '{rosdistro_name}' in ros/rosdistro")
    return tags[-1]


def main():
    parser = argparse.ArgumentParser(
        description="Generate a package.xml with all the recursive build, buildtool, build_export, buildtool_export, exec, run and test dependencies as exec depends"
    )
    parser.add_argument(
        "--rosdistro",
        type=str,
        required=True,
        choices=("noetic", "foxy", "humble", "jazzy", "lyrical"),
        help="The ROS distro to evaluate.",
    )
    parser.add_argument(
        "--variant",
        type=str,
        required=True,
        choices=(
            "desktop",
            "desktop-full",
            "perception",
            "robot",
            "ros-base",
            "ros-core",
        ),
        help="The ROS (install) metapackage to serve as a variant. (default: %(default)s).",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        type=str,
        required=True,
        help="package.xml file to write for dependencies",
    )
    parser.add_argument(
        "-c",
        "--cmake-file",
        type=str,
        required=True,
        help="CMakeLists.txt file to write for metapackages",
    )

    args = parser.parse_args()

    # We get the index from the latest tag and not from master which is not synced.
    # For lyrical (not tagged yet), get_latest_rosdistro_tag falls back to "master".
    latest_tag = get_latest_rosdistro_tag(args.rosdistro)
    index = rosdistro.get_index(
        f"https://raw.githubusercontent.com/ros/rosdistro/{latest_tag}/index-v4.yaml"
    )

    upstream_distribution = rosdistro.get_distribution(index, args.rosdistro)

    dependency_walker = DependencyWalker(upstream_distribution)

    target_pkg = args.variant.replace("-", "_")

    try:
        ignore_pkgs = [
            "rmw_connextdds",
            "rmw_connext_cpp",
            "connext_dds_cmake_module",
            "rmw_cyclonedds_cpp",
            "rosidl_typesupport_connext_c",
            "rosidl_typesupport_connext_cpp",
        ]

        target_pkg_rec_deps = dependency_walker.get_recursive_depends(
            target_pkg,
            [
                "build",
                "build_export",
                "buildtool",
                "buildtool_export",
                "exec",
                "run",
                "test",
            ],
            ros_packages_only=True,
            ignore_pkgs=ignore_pkgs,
        )
    except KeyError as e:
        print(
            f"Caught the following error while walking dependencies of {target_pkg}:\n {e}"
        )
        sys.exit(1)

    meta_package = PackageTemplate._create_package_template(
        package_name=f"meta-{args.variant}", licenses=["GPLv3"]
    )
    if args.rosdistro != "noetic":
        meta_package.buildtool_depends = [Dependency("ament_cmake")]
        # @todo <export><build_type>ament_cmake</build_type></export>
    for d in target_pkg_rec_deps:
        meta_package.exec_depends.append(Dependency(d))

    meta_package_xml = create_package_xml(meta_package, args.rosdistro, meta=True)
    with open(args.output_file, "w") as f:
        f.write(meta_package_xml)

    if args.rosdistro != "noetic":
        with open(args.cmake_file, "w") as f:
            f.write(f"""
cmake_minimum_required(VERSION 3.5)
project(meta-{args.variant} NONE)
find_package(ament_cmake REQUIRED)
ament_package()
""")
    else:
        with open(args.cmake_file, "w") as f:
            f.write(create_cmakelists(meta_package, args.rosdistro, meta=True))


if __name__ == "__main__":
    main()
