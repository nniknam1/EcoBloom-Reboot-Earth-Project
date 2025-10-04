import webbrowser
import os

# Get the directory of the current Python script.
script_dir = os.path.dirname(os.path.abspath(__file__))

# Specify the name of your HTML file.
html_filename = 'heat_stress_detection.html'

# Create the full, absolute path to the HTML file.
file_path = os.path.join(script_dir, html_filename)

# Use the file:// URI scheme to open the local file.
webbrowser.open('file://' + file_path)

print(f"Opening {file_path} in your default browser...")