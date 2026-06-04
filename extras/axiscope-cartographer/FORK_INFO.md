# Fork information

This repository is a maintained fork of Axiscope Cartographer for a StealthChanger / KTC-Easy printer using Cartographer touch probing.

## Source

- Upstream project: https://github.com/buddasticks/Axiscope-cartographer
- Maintained fork: https://github.com/Batcandoionline/Axiscope-cartographer
- Original license: MIT, preserved in `LICENSE`

## Current printer stack

Captured from the printer Update Manager on 2026-05-16:

- axiscope: `v0.0.0-13-ga34a956b-inferred`
- Cartographer Plugin: `1.6.0`
- Klipper: `v0.13.0-650-gca8230d5`
- Moonraker: `v0.10.0-20-g90084858`
- Mainsail: `v2.17.0`
- klipper-toolchanger-easy: `v0.0.0-250-g5f0e5a3f-inferred`

## Local changes

- Cartographer Z probing reads `cartographer.touch.last_z_result`.
- The invalid fallback to current toolhead Z was removed to prevent false `2.000` Z results.
- Installer defaults to this fork so Moonraker Update Manager can update it directly.
