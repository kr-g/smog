import subprocess

from run_freeze import load_requirements_versions_cleared


def upgrade_requirements_packages():

    packages = load_requirements_versions_cleared()

    for p in packages:
        args = [
            "python3",
            "-m",
            "pip",
            "install",
            p,
            "-U",
        ]
        print("running", args)

        proc = subprocess.Popen(args, stdout=subprocess.PIPE)
        while True:
            line = proc.stdout.readline()
            if len(line) == 0:
                break
            print(line.decode().strip())


if __name__ == "__main__":
    upgrade_requirements_packages()
