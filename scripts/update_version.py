import subprocess

import toml


def get_latest_tag():
    result = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"], capture_output=True, text=True
    )
    return result.stdout.strip().lstrip("v")


def update_pyproject_version(version):
    pyproject_path = "pyproject.toml"
    with open(pyproject_path, "r") as f:
        data = toml.load(f)

    data["tool"]["poetry"]["version"] = version

    with open(pyproject_path, "w") as f:
        toml.dump(data, f)


def update_version_file(version):
    version_path = "src/friday/version.py"
    with open(version_path, "w") as f:
        f.write(f'__version__ = "{version}"\n')


if __name__ == "__main__":
    version = get_latest_tag()
    update_pyproject_version(version)
    update_version_file(version)
