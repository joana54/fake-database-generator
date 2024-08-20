import subprocess, sys

def install_packages(package):
    """
    Install Python packages using pip.

    Args:
    package (str or list): A single package name as a string or a list of package names.

    Returns:
    None
    """
    if type(package) == str:
        # Install a single package
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    elif type(package) == list:
        # Install multiple packages
        for pack in package:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pack])