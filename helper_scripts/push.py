import argparse
import os
import glob
import subprocess
import sys
from pathlib import Path

import requests


def create_parser():
    parser = argparse.ArgumentParser(
        "Copy configuration files to home-assistant in k8s"
    )
    parser.add_argument("--reload", default=False, action="store_true")
    parser.add_argument("--dry_run", default=False, action="store_true")
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    last_push_file = Path(".last_push")
    if not os.path.exists(".last_push"):
        print("No last_push file found, creating a new one.")
        last_push_file.touch()
        last_modified_timestamp = 0
    else:
        last_modified_timestamp = last_push_file.stat().st_mtime

    recurs_folders = ["automations", "entities"]
    config_folder = "."

    configuration_files = [
        os.path.join(i)
        for i in os.listdir(config_folder)
        if ".yaml" in i and Path(i).stat().st_mtime > last_modified_timestamp
    ]
    other_files = []

    for folder in recurs_folders:
        for filename in glob.iglob(f"{folder}/**/*", recursive=True):
            if Path(filename).stat().st_mtime > last_modified_timestamp:
                if ".yaml" in filename:
                    other_files.append(filename)

    print("Config files to push:")
    print(configuration_files)
    print("")
    print("Other files to push:")
    print(other_files)
    if args.dry_run:
        sys.exit()

    print("Getting pods")
    pods = subprocess.run("kubectl get pods".split(), stdout=subprocess.PIPE)
    pod_data = next(
        (i for i in pods.stdout.decode("utf-8").split("\n") if "home-assistant" in i),
        None,
    )
    pod_name = pod_data.split()[0]
    print(f"Got pod {pod_name}")

    all_files = configuration_files + other_files
    if not all_files:
        print("No changes detected.")
        sys.exit(0)

    print("Copying files")
    for file in all_files:
        cmd = f"kubectl cp {file} {pod_name}:/config/{file}"
        print(cmd)
        result = subprocess.run(
            cmd.split(),
            stdout=subprocess.PIPE,
        )
        if result.returncode == 0:
            print(f"{file} OK")

    last_push_file.touch()

    # Hard reload
    if args.reload:
        print("Deleting pod (may take a while for subprocess to finish)")
        result = subprocess.run(
            f"kubectl delete pods {pod_name}".split(), stdout=subprocess.PIPE
        )
        if result.returncode == 0:
            print("Deleted home-assistant pod")

    # Soft reload services
    else:
        url = "https://homeassistant.homelab.jph.dev/api/services"
        headers = {
            "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIwMWE0OTZkNjYzODE0MzE4YWMxNjQwMDAzYWY3YjgwNyIsImlhdCI6MTYyNTY3NjkxNSwiZXhwIjoxOTQxMDM2OTE1fQ.48gj13U3T_9bX0FsDSQ2UbjLeyVR0GITZ1-uRLvVP6Q",
            "Content-Type": "application/json",
        }
        services = [
            i["domain"] for i in requests.get(url.format(url), headers=headers).json()
        ]

        reload_targets = []

        for service in services:
            if [i for i in all_files if service in i]:
                reload_targets.append(service)

        for target in reload_targets:
            result = requests.post(f"{url}/{target}/reload", headers=headers)
            if not result.ok:
                print(f"Failed to reload {target}")
            else:
                print(f"Reloaded {target}")


if __name__ == "__main__":
    main()
