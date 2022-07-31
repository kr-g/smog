from setuputil import *
import setuptools

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
    entry_points=entry_points,
)

print(f"using python version: {pyversion}")


# python3 -m setup sdist build bdist_wheel

# test.pypi
# twine upload --repository testpypi dist/*
# python3 -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ smog

# pypi
# twine upload dist/*
