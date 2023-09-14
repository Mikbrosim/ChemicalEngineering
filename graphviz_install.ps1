# Define the URL of the zip file
$zipUrl = "https://gitlab.com/api/v4/projects/4207231/packages/generic/graphviz-releases/9.0.0/windows_10_msbuild_Release_graphviz-9.0.0-win32.zip"

# Define the file name for the downloaded zip file
$zipFileName = "graphviz-9.0.0-win32.zip"

# Define the directory where you want to extract the contents
$extractPath = (Get-Location)

# Download the zip file
Invoke-WebRequest -Uri $zipUrl -OutFile $zipFileName

# Unzip the downloaded file into the current working directory
Expand-Archive -Path $zipFileName -DestinationPath $extractPath

# Clean up: remove the downloaded zip file (optional)
Remove-Item -Path $zipFileName

python -m pip -r pydot
python -m pip -r sympy
