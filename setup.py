import setuptools
import os
import re


def find_version(fnam, version="VERSION"):
    with open(fnam) as f:
        cont = f.read()
    regex = f'{version}\s*=\s*["]([^"]+)["]'
    match = re.search(regex, cont)
    if match is None:
        raise Exception(
            f"version with spec={version} not found, use double quotes for version string"
        )
    return match.group(1)


def find_projectname():
    cwd = os.getcwd()
    name = os.path.basename(cwd)
    return name


file = os.path.join("smog", "smog.py")
version = find_version(file)
projectname = find_projectname()

setuptools.setup(
    name=projectname,
    version=version,
    author="k. goger",
    author_email=f"k.r.goger+{projectname}@gmail.com",
    url=f"https://github.com/kr-g/{projectname}",
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "SQLAlchemy",
        "python-xmp-toolkit",
        "python-dateutil",
    ],
    entry_points={
        "console_scripts": [f"{projectname} = {projectname}.{projectname}:main_func"],
    },
)

# python3 -m setup sdist build bdist_wheel
# twine upload dist/*
