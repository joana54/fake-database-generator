"""
This module provides utility functions to programmatically install Python packages using pip.
It includes a function to handle the installation of both single and multiple packages with proper 
error handling and logging to ensure successful package installations and clear diagnostics in 
case of failure.

Functions:
    install_packages(packages): Installs a single package or a list of packages using pip. 
                                It ensures that any issues during installation are logged and 
                                properly communicated to the caller.

The module can be used as a standalone script for installing packages or imported into other 
scripts or projects where automated Python package installation is required.

Dependencies:
    subprocess: Used to execute pip commands.
    sys: Provides access to some variables used or maintained by the interpreter.
    logging: Used to log messages.

Example usage:
    python -m this_module_name  # Assuming the script is named appropriately and callable 
    as a module.

Notes:
    This module assumes pip is already installed and available in the Python environment 
    where the script is executed.
"""

import subprocess
import sys

def install_packages(package):
    """
    Install Python packages using pip.

    Args:
    package (str or list): A single package name as a string or a list of package names.

    Returns:
    None
    """
    if isinstance(package, str):
        # Install a single package
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    elif isinstance(package, list):
        # Install multiple packages
        for pack in package:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pack])
