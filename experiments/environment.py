"""Record software versions for reproducibility without saving credentials."""

import json
import os
import platform
import subprocess
from pathlib import Path
from urllib.request import urlopen

import matplotlib
import numpy
import sklearn


def version(command):
    try:
        return subprocess.run(command, capture_output=True, text=True, timeout=10,
                              check=True).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "unavailable"


def main():
    try:
        with urlopen("http://127.0.0.1:11434/api/version", timeout=5) as response:
            ollama = json.load(response).get("version", "unknown")
        with urlopen("http://127.0.0.1:11434/api/tags", timeout=5) as response:
            models = {row["name"]: row.get("digest") for row in json.load(response).get("models", [])}
    except OSError:
        ollama, models = "unavailable", {}
    output = {
        "platform": platform.platform(), "processor": platform.processor(),
        "logical_cpu_count": os.cpu_count(),
        "controller_python": platform.python_version(),
        "sandbox_python": version(["/usr/bin/python3", "--version"]),
        "numpy": numpy.__version__, "scikit_learn": sklearn.__version__,
        "matplotlib": matplotlib.__version__,
        "bubblewrap": version(["bwrap", "--version"]),
        "ollama": ollama,
        "installed_model_digests": models,
    }
    path = Path("results/environment.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
