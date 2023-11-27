import os
import urllib.request
import zipfile

# Define the URL of the zip file
zip_url = "https://gitlab.com/api/v4/projects/4207231/packages/generic/graphviz-releases/9.0.0/windows_10_msbuild_Release_graphviz-9.0.0-win32.zip"

# Define the file name for the downloaded zip file
zip_filename = "graphviz-9.0.0-win32.zip"

# Define the directory where you want to extract the contents
extract_path = os.getcwd()

# Download the zip file
urllib.request.urlretrieve(zip_url, zip_filename)

# Unzip the downloaded file into the current working directory
with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
    zip_ref.extractall(extract_path)

# Clean up: remove the downloaded zip file (optional)
os.remove(zip_filename)

# Install the required packages using pip
os.system("python -m pip install sympy pydot pillow tkinter")