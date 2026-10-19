# A tool that picks the format — "Image workshop" for Open WebUI and ComfyUI

Demo code for module 4 of the "Click by Click" series **Image generation in Open WebUI with
ComfyUI**. In Open WebUI, the built-in image generation tool only receives a description: every
image has the size set on the Images page, the same for the whole instance. The home-made tool
**"Image workshop"** lets the chat model choose the **format** (poster, banner, square thumbnail)
and the **number of variants**, while reusing the organization's ComfyUI workflow and node mapping
(style guide included).

Video: {{video}}

## Goal

- Read Open WebUI 0.11's built-in tool `generate_image` (`open_webui/tools/builtin.py`): a single
  parameter, no size; images attached to the message, an "already visible" answer to the model.
- Write an Open WebUI tool (`open-webui/image_workshop.py`, version 1):
  - `FORMATS`: poster 832 × 1216, banner 1536 × 640, square 1024 × 1024;
  - a valve `max_variants` (1 by default, 3 in the video);
  - a single function offered to the model, `create_visual(description, format, variants)`,
    whose format is an enumeration (`Literal`) and whose parameters are each described for the
    model;
  - the right to generate images checked as for the built-in tool, a progress message, one
    generation per variant (Open WebUI's `image_generations`, at the format's size), the images
    attached to the message and shown, an answer that keeps the model from repeating them.
- Install it, set its valve, attach it to an "Image workshop" model; check in the tool calls what
  the model chose.

| File | Content |
|---|---|
| `open-webui/image_workshop.py` | The tool, **English version** of the `atelier_images.py` pasted in the French video (same structure, same blocks; `create_visual`, formats `poster`, `banner`, `square`, valve `max_variants`), as shown in the English and German videos |
| `open-webui/workshop-instructions.txt` | The system prompt of the "Image workshop" model (`workshop-instructions.de.txt`: German version) |
| `open-webui/workshop-model.md` | Settings of the model and of the tool, what the model sees |
| `setup_workshop.py` | Tool and model installed through Open WebUI's API, check, removal |
| `workflows/posters-v2.json` | The organization's workflow (module 2) that the tool reuses, in API format |

## Prerequisites

- The image server of modules 1 and 2: ComfyUI v0.41 on a graphics card, connected to Open WebUI
  0.11 (Images page, workflow `posters-v2`, node mapping `string_b` / 34) —
  [`clic-par-clic-comfyui-01-brancher`](https://github.com/guilhem-/clic-par-clic-comfyui-01-brancher),
  [`clic-par-clic-comfyui-02-workflow-organisation`](https://github.com/guilhem-/clic-par-clic-comfyui-02-workflow-organisation).
  The tool has **no setting of its own for the image server**: it goes through the Images page.
- An Open WebUI **administrator** account (tools run code on the server: only an administrator,
  or an authorized user, can create one).
- A chat model able to call tools ("native" function calling, Open WebUI 0.11's default setting).
- For the users: image generation turned on in the Images page, and the "Image Generation"
  permission (module 5).

## Step by step

### 1. By hand, as in the video

1. **Workspace › Tools › "+"**: name `Image workshop`, id `image_workshop`, paste the content of
   `open-webui/image_workshop.py`, **Access**: public (a user can only use a tool they have access
   to), **Save & Create**, confirm.
2. In the list of tools, the **Valves** gear of the tool: `max_variants` to `3`, **Save**.
3. **Workspace › Models › "+"**: name `Image workshop`, base model, system prompt =
   `open-webui/workshop-instructions.txt`, **Tools**: tick "Image workshop", **Access**: public (or a
   group), **Save & Create**.

### 2. Through the API

```bash
cp .env.example .env                 # OWUI_URL, OWUI_TOKEN (administrator), BASE_MODEL
python setup_workshop.py             # creates or updates the tool, its valve and the model
python setup_workshop.py --check     # functions seen by the model, formats, valve, tools of the model
python setup_workshop.py --remove    # deletes the model, then the tool
```

## Try it

With a user account, new chat with the **Image workshop** model (without turning on "Image": the
tool is attached to the model):

1. "Prepare the poster for the Workplace Safety training in Lyon, and a banner to announce it on
   the intranet." — two calls of `create_visual`, one per format: a portrait image, a very wide one.
2. "Suggest three square versions for the internal newsletter thumbnail." — one call, format
   `square`, `variants`: 3; three images, three seeds.

Unfold the tool calls to read the arguments chosen by the model.

## Good to know

- **A variant is a full computation** (about thirty seconds per image on an 8 GB card): three
  variants, three times the time. The valve protects ComfyUI's queue.
- **The style guide** is in the workflow (module 2): it applies to every format, whatever the text
  written by the model.
- **Private methods**: Open WebUI offers the model every public method of the `Tools` class. The
  helper functions (`_allowed`, `_generate`, `_status`) start with `_` to stay invisible.
- **Code that evolves**: version 2 (module 6) adds the image charter check before the loop;
  version 3 (module 8) replaces `_generate` to mark the images.
- **The built-in tool** stays available with the "Image" switch.
- **Alternative**: one Pipe function per workflow, which shows up as a model in the list; the user
  chooses, the chat model does not step in.

## Series

- Previous module: **Editing an image** —
  [`clic-par-clic-comfyui-03-retouche`](https://github.com/guilhem-/clic-par-clic-comfyui-03-retouche).
- Next module: **Who can generate images?** (permissions per group) —
  [`clic-par-clic-comfyui-05-droits-groupes`](https://github.com/guilhem-/clic-par-clic-comfyui-05-droits-groupes).

## License

MIT (see `LICENSE`). ComfyUI: GPL-3.0; Z-Image Turbo: Apache 2.0; Open WebUI: its own license (the
code quoted in the video stays theirs and is not copied here).
