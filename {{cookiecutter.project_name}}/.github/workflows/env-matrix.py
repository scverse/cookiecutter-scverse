# /// script
# requires-python = ">=3.11"
# dependencies = [ "packaging", "hatch" ]
# ///

import json
from pathlib import Path
from subprocess import check_output

import tomllib
from packaging.specifiers import Specifier

conf = tomllib.loads(Path("pyproject.toml").read_text())
spec = Specifier(conf["project"]["requires-python"])
envs = json.loads(check_output(["hatch", "env", "show", "--json"]))
matrix = dict(
    include=[
        dict(
            name=(
                f"{env_name} (PRE-RELEASE DEPENDENCIES)"
                if "pre" in env_name.split(".")
                else env_name
            ),
            env_name=env_name,
            python=env["python"],
        )
        for env_name, env in envs.items()
        if env_name.startswith("hatch-test")
        if spec.contains(env["python"])
    ]
)
print(json.dumps(matrix))
