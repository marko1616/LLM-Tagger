import argparse

from pathlib import Path
from getpass import getpass
from string import Template

template_sources = [
    Path(__file__).parent / "backend" / "templates" / "config.json.template",
    Path(__file__).parent / "frontend" / "templates" / "config.json.template"
]

template_targets = [
    Path(__file__).parent / "backend" / "config.json"
    , Path(__file__).parent / "frontend" / "public" / "config.json"
]

def apply_config_template(template_source: Path, template_target: Path, api_base: str, api_token: str):
    with open(template_source, "r") as template_file:
        print(f"Applying template {template_source} to {template_target}")
        template = Template(template_file.read()).substitute(api_base=api_base, api_token=api_token)
    
    with open(template_target, "w") as target_file:
        target_file.write(template)

def setup():
    print("Setting up project...")
    url_base = input("Enter the urlbase for the project(eg. http://localhost:8000):")
    url_base = url_base if url_base.endswith("/") else url_base + "/"
    api_base = url_base + "api/"
    api_token = getpass("Enter the API token for the project:")
    for template, target in zip(template_sources, template_targets):
        apply_config_template(template, target, api_base, api_token)
    print("To deploy the project, run the following command:")
    print(f"sudo docker compose build --no-cache")
    print(f"sudo docker compose up -d")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI for managing project.")
    parser.add_argument("operate", type=str, help="Operation to perform.")

    args = parser.parse_args()
    if args.operate == "setup":
        setup()
    else:
        print("Invalid operation.")
        exit(1)