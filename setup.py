import platform
import os
import importlib
import re
import setuptools


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


def load_requirements():
    with open("requirements.txt") as f:
        lines = f.readlines()
        lines = map(lambda x: x.strip(), lines)
        lines = filter(lambda x: len(x) > 0, lines)
        lines = filter(lambda x: x[0] != "#", lines)
        return list(lines)


def get_scripts(projectname):
    console_scripts = []
    gui_scripts = []

    try:
        mod = importlib.import_module(f"{projectname}.__main__")
        if "main_func" in dir(mod):
            console_scripts = [
                f"{projectname} = {projectname}.__main__:main_func",
            ]
        if "gui_func" in dir(mod):
            gui_scripts = [
                f"{projectname}-ui = {projectname}.__main__:gui_func",
            ]
    except:
        pass

    return console_scripts, gui_scripts


pyver = platform.python_version_tuple()[:2]
pyversion = ".".join(pyver)

projectname = find_projectname()
file = os.path.join(projectname, "const.py")
version = find_version(file)

console_scripts, gui_scripts = get_scripts(projectname)

#

setuptools.setup(
    name=projectname,
    version=version,
    author="k. goger",
    author_email=f"k.r.goger+{projectname}@gmail.com",
    url=f"https://github.com/kr-g/{projectname}",
    packages=setuptools.find_packages(
        exclude=[
            "tests",
            "docs",
        ]
    ),
    python_requires=f">={pyversion}",
    install_requires=load_requirements(),
    entry_points={
        "console_scripts": console_scripts,
        "gui_scripts": gui_scripts,
    },
)

print(f"using python version: {pyversion}")


# python3 -m setup sdist build bdist_wheel

# test.pypi
# twine upload --repository testpypi dist/*
# python3 -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ smog

# pypi
# twine upload dist/*
