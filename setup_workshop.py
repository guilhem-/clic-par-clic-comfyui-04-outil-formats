"""Install the "Image workshop" tool and the model of the same name in Open WebUI, through its API.

Does what module 4 of the "Image generation in Open WebUI with ComfyUI" series does on screen,
in the workspace:
  1. creates (or updates) the image_workshop tool with the code of open-webui/image_workshop.py,
     open to every user;
  2. sets its valve: max_variants = 3;
  3. creates (or updates) the image-workshop model: base model, instructions
     (open-webui/workshop-instructions.txt), tool ticked, open to every user.
The Images page (workflow, node mapping, image model) is not touched: the tool uses the one of the
organization's image server (modules 1 and 2).

Usage:
  python setup_workshop.py             # install or update the tool and the model
  python setup_workshop.py --check     # check: tool, schema read by the model, valve, model
  python setup_workshop.py --remove    # delete the model, then the tool

Settings: .env file (see .env.example); environment variables take precedence.
No dependency: Python 3.10 or newer, standard library only.
"""
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
CODE = HERE / "open-webui" / "image_workshop.py"
INSTRUCTIONS = HERE / "open-webui" / "workshop-instructions.txt"
VARIABLES = ("OWUI_URL", "OWUI_TOKEN", "BASE_MODEL", "MAX_VARIANTS")

TOOL = {"id": "image_workshop", "name": "Image workshop"}
MODEL = {"id": "image-workshop", "name": "Image workshop"}
# Open to every user (read): a user can only use a tool they have access to.
# To be reserved for a group in module 5.
PUBLIC = [{"principal_type": "user", "principal_id": "*", "permission": "read"}]


def settings() -> dict:
    """Defaults, then .env (key=value), then the environment, which wins."""
    s = {"OWUI_URL": "http://127.0.0.1:8080", "MAX_VARIANTS": "3"}
    env = HERE / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                s[key.strip()] = value.strip()
    for key in VARIABLES:
        if os.environ.get(key):
            s[key] = os.environ[key]
    return s


S = settings()


def api(method: str, path: str, body=None, tolerate=False):
    """Call Open WebUI's API with an administrator token."""
    if not S.get("OWUI_TOKEN"):
        sys.exit("OWUI_TOKEN missing (.env): token of an Open WebUI administrator account.")
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        S["OWUI_URL"].rstrip("/") + path, data=data, method=method,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {S['OWUI_TOKEN']}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            text = resp.read().decode()
    except urllib.error.HTTPError as e:
        if tolerate:
            return None
        sys.exit(f"{method} {path}: {e.code} {e.read().decode()[:300]}")
    return json.loads(text) if text.strip() else None


def install() -> None:
    if not S.get("BASE_MODEL"):
        sys.exit("BASE_MODEL missing (.env): id of the chat model (able to call tools).")
    code = CODE.read_text(encoding="utf-8")
    tool = {"id": TOOL["id"], "name": TOOL["name"], "content": code, "meta": {"description": "", "manifest": {}}, "access_grants": PUBLIC}
    if api("GET", f"/api/v1/tools/id/{TOOL['id']}", tolerate=True):
        api("POST", f"/api/v1/tools/id/{TOOL['id']}/update", tool)
        print(f"Tool {TOOL['id']} updated.")
    else:
        api("POST", "/api/v1/tools/create", tool)
        print(f"Tool {TOOL['id']} created.")
    api("POST", f"/api/v1/tools/id/{TOOL['id']}/valves/update", {"max_variants": int(S["MAX_VARIANTS"])})
    print(f"Valve max_variants = {S['MAX_VARIANTS']}.")

    model = {
        "id": MODEL["id"], "name": MODEL["name"], "base_model_id": S["BASE_MODEL"],
        "meta": {"profile_image_url": "/static/favicon.png", "description": "Visuals in the organization's formats", "toolIds": [TOOL["id"]]},
        "params": {"system": INSTRUCTIONS.read_text(encoding="utf-8").strip()},
        "access_grants": PUBLIC,
    }
    if api("GET", f"/api/v1/models/model?id={MODEL['id']}", tolerate=True):
        api("POST", "/api/v1/models/model/update", model)
        print(f"Model {MODEL['id']} updated.")
    else:
        api("POST", "/api/v1/models/create", model)
        print(f"Model {MODEL['id']} created (base: {S['BASE_MODEL']}).")


def check() -> None:
    tool = api("GET", f"/api/v1/tools/id/{TOOL['id']}", tolerate=True)
    if not tool:
        sys.exit(f"Tool {TOOL['id']} absent.")
    specs = {s["name"]: s for s in tool.get("specs", [])}
    if list(specs) != ["create_visual"]:
        print(f"Warning: functions offered to the model: {list(specs)} (expected: create_visual only)")
    properties = specs.get("create_visual", {}).get("parameters", {}).get("properties", {})
    print("Formats offered to the model:", properties.get("format", {}).get("enum"))
    print("Valves:", api("GET", f"/api/v1/tools/id/{TOOL['id']}/valves"))
    model = api("GET", f"/api/v1/models/model?id={MODEL['id']}", tolerate=True)
    if not model:
        sys.exit(f"Model {MODEL['id']} absent.")
    print("Tools of the model:", model.get("meta", {}).get("toolIds"))
    config = api("GET", "/api/v1/images/config")
    if not config.get("ENABLE_IMAGE_GENERATION") or config.get("IMAGE_GENERATION_ENGINE") != "comfyui":
        print("Warning: image generation is not connected to ComfyUI (Images page).")


def remove() -> None:
    api("POST", "/api/v1/models/model/delete", {"id": MODEL["id"]}, tolerate=True)
    api("DELETE", f"/api/v1/tools/id/{TOOL['id']}/delete", tolerate=True)
    print("Model and tool removed.")


if __name__ == "__main__":
    actions = {"--check": check, "--remove": remove}
    actions.get(sys.argv[1] if len(sys.argv) > 1 else "", install)()
