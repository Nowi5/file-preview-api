import glob
import os
import pathlib
import subprocess
import sys

# Places we might find a Python install:
possible_python_paths = []

if os.name in ("nt", "os2"):
    if "PROGRAMFILES" in list(os.environ.keys()):
        possible_python_paths += glob.glob(
            os.environ["PROGRAMFILES"] + "\\LibreOffice*"
        )

    if "PROGRAMFILES(X86)" in list(os.environ.keys()):
        possible_python_paths += glob.glob(
            os.environ["PROGRAMFILES(X86)"] + "\\LibreOffice*"
        )

    if "PROGRAMW6432" in list(os.environ.keys()):
        possible_python_paths += glob.glob(
            os.environ["PROGRAMW6432"] + "\\LibreOffice*"
        )

elif sys.platform == "darwin":
    possible_python_paths += ["/Applications/LibreOffice.app/Contents"]
else:
    possible_python_paths += [
        "/usr/bin",
        "/usr/local/bin",
        "~/.local/bin",
    ]
    possible_python_paths += (
        glob.glob("/usr/lib*/libreoffice*")
        + glob.glob("/opt/libreoffice*")
        + glob.glob("/usr/local/lib/libreoffice*")
        + glob.glob(os.path.expanduser("./local/lib/libreoffice*"))
    )

found_pythons = []

for python_path in possible_python_paths:
    path = pathlib.Path(os.path.expanduser(python_path))
    for python in path.rglob("python3"):
        if not python.is_dir() and os.access(python, os.X_OK):
            found_pythons.append(str(python))
    for python in path.rglob("python"):
        if not python.is_dir() and os.access(python, os.X_OK):
            found_pythons.append(str(python))


pythons_with_libreoffice = []
for python in found_pythons:
    print(f"Trying python found at {python}", end="...")
    proc = subprocess.run(
        [python, "-c", "import uno;from com.sun.star.beans import PropertyValue"],
        stderr=subprocess.PIPE,
    )
    if proc.returncode:
        print(" Failed")
    else:
        print(" Success!")
        pythons_with_libreoffice.append(python)

print(f"Found {len(pythons_with_libreoffice)} Pythons with Libreoffice libraries:")
for python in pythons_with_libreoffice:
    print(python)
