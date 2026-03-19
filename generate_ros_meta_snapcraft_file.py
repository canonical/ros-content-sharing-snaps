import argparse
import os
import shutil
import subprocess

from pathlib import Path

import jinja2


def main(args=None):
    parser = argparse.ArgumentParser(
        description="Generate a snapcraft.yaml file for a ROS foundational snap."
    )
    parser.add_argument(
        "-r",
        "--rosdistro",
        type=str,
        required=True,
        choices=("noetic", "foxy", "humble", "jazzy"),
        help="The ROS distro to target.",
    )
    parser.add_argument(
        "-v",
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
        default="ros-core",
        help="The ROS metapackage to serve as a baseline. (default: %(default)s).",
    )
    parser.add_argument(
        "-a",
        "--architecture",
        type=str,
        required=False,
        choices=("amd64", "arm64", "armhf"),
        help="Deprecated. Architecture is no longer used in template generation.",
    )
    parser.add_argument(
        "-p",
        "--path",
        # type=is_dir,
        required=False,
        # default="",
        help="Output path for generated files.",
    )
    parser.add_argument("-s", "--snap", help="Run snapcraft.", action="store_true")
    parser.add_argument(
        "-d", "--dev", help="Generate the dev snap.", action="store_true"
    )
    parser.add_argument("-q", "--quiet", help="Do not print.", action="store_true")

    parsed_args = parser.parse_args(args=args)

    if parsed_args.snap:
        if not parsed_args.path:
            raise ValueError("Option '--path' must be set when using '--snap'!")

    template_name = "snapcraft.yaml.j2"

    with open(Path("templates") / template_name, "r") as f:
        environment = jinja2.Environment()
        environment.filters["bool"] = bool
        template = environment.from_string(f.read())
        snapcraft_file = template.render(
            ros_distro=parsed_args.rosdistro,
            variant=parsed_args.variant,
            dev=parsed_args.dev,
        )
        if not parsed_args.quiet:
            print(snapcraft_file)
        if parsed_args.path:
            if not (
                os.path.exists(parsed_args.path) and os.path.isdir(parsed_args.path)
            ):
                raise IsADirectoryError(f"{parsed_args.path} is not a directory!")
            with open(Path(parsed_args.path) / "snapcraft.yaml", "w") as f:
                f.write(snapcraft_file)
            if parsed_args.snap:
                subprocess.run(
                    ["snapcraft", "--use-lxd", "--verbose"],
                    check=True,
                )

        # add the generate_package_xml_recursive_dependencies.py in case of a dev snap
        if parsed_args.dev:
            shutil.copy2(
                "generate_package_xml_recursive_dependencies.py", f"{parsed_args.path}"
            )

        return snapcraft_file


if __name__ == "__main__":
    main()
