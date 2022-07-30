from run_freeze import bump_requirements
from run_autodoc import create_autodoc
from run_upgrade import upgrade_requirements_packages

if __name__ == "__main__":
    upgrade_requirements_packages()
    create_autodoc()
    bump_requirements()
