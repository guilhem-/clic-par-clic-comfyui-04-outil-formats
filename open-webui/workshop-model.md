# "Image workshop" model — settings

Created in Open WebUI › Workspace › Models › "+" (or by `python setup_workshop.py`).

| Field | Value |
|---|---|
| Name | `Image workshop` |
| Id | `image-workshop` (suggested by the interface from the name) |
| Base model | the organization's usual chat model, able to call tools ("native" function calling, Open WebUI 0.11's default setting) |
| System prompt | the text of [`workshop-instructions.txt`](workshop-instructions.txt) (German: [`workshop-instructions.de.txt`](workshop-instructions.de.txt)) |
| Tools | **Image workshop** ticked (`image_workshop`) |
| Capabilities | the default ones; the "Image" switch is not needed: the tool is attached to the model |
| Access | public (read for every user); reserved for a group in module 5 |

## "Image workshop" tool

| Field | Value |
|---|---|
| Name | `Image workshop` |
| Id | `image_workshop` (the interface suggests it from the name; the next modules refer to it) |
| Code | [`image_workshop.py`](image_workshop.py), pasted into the editor |
| Access | public: a user can only use a tool they have access to, even when it is attached to a model (reserved for a group in module 5) |
| Valve `max_variants` | `3` (default: `1`) |

## What the model sees

One function only, `create_visual` (methods whose name starts with `_` are not offered to the
model):

- `description` (text): what the image shows, without text or style;
- `format`: enumeration `poster`, `banner`, `square` (Python `Literal` type, converted into an
  `enum` in the tool's JSON schema);
- `variants` (integer, 1 by default), capped by the valve.

The sizes (`FORMATS`): poster 832 × 1216, banner 1536 × 640, square 1024 × 1024 — multiples of 64,
about one million pixels each, which the organization's image model computes in about thirty
seconds on an 8 GB card.
