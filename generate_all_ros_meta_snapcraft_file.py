import argparse
import os
from pathlib import Path
from typing import List

from generate_ros_meta_snapcraft_file import main as gen

class ROSContentSharingSnapVariants:
    """Represent all the content sharing snaps to generate."""
    def __init__(self, *, ros_distro: str, variants: List[str], architectures: List[str]):
        self.ros_distro = ros_distro
        self.variants = variants
        self.architectures = architectures

def is_dir(path: str) -> Path:
    if os.path.exists(path) and os.path.isdir(path):
        return Path(path)
    raise OSError(f"{path} is not a directory!")

def main(args=None):
    parser = argparse.ArgumentParser(
        description="Generate a snapcraft.yaml file for all ROS foundational snap."
    )
    parser.add_argument(
        "-p",
        "--path",
        type=is_dir,
        required=False,
        help="Output path for generated files.",
    )
    parser.add_argument(
        "-s",
        "--snap",
        help="Run snapcraft for the generated files.",
        action="store_true"
    )

    parsed_args = parser.parse_args(args=args)

    if not parsed_args.path:
        parsed_args.path = Path("snaps")
        os.makedirs(parsed_args.path, exist_ok=True)

    ros_distros_content_sharing_snaps = [
        # ROSContentSharingSnapVariants(
        #     ros_distro = "noetic",
        #     variants = ["ros-core", "ros-base", "robot", "desktop"],
        #     architectures = ["amd64", "arm64"]),
        ROSContentSharingSnapVariants(
            ros_distro = "foxy",
            variants = ["ros-core", "ros-base", "desktop"],
            architectures = ["amd64", "arm64"]),
        ROSContentSharingSnapVariants(
            ros_distro = "humble",
            variants = ["ros-core", "ros-base", "desktop"],
            architectures = ["amd64", "arm64"]),
        ROSContentSharingSnapVariants(
            ros_distro = "jazzy",
            variants = ["ros-core", "ros-base", "desktop"],
            architectures = ["amd64", "arm64"]),
        ]

    for distro_content_sharing_snap in ros_distros_content_sharing_snaps:
        for variant in distro_content_sharing_snap.variants:
            for architecture in distro_content_sharing_snap.architectures:
                ros_distro = distro_content_sharing_snap.ros_distro
                folders = [
                    parsed_args.path / f'{ros_distro}-{variant}-{architecture}',
                    parsed_args.path / f'{ros_distro}-{variant}-dev-{architecture}'
                ]

                for folder in folders:
                    os.makedirs(folder, exist_ok=True)
                    gen_args = ["-r", ros_distro, "-v", variant, "-a", architecture, "-p", str(folder), "-q"]
                    if "dev" in folder.stem:
                        gen_args.append("-d")
                    if parsed_args.snap:
                        gen_args.append("-s")

                    gen(gen_args)


if __name__ == "__main__":
    main()
