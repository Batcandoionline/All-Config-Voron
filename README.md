# All-Config-Voron

Main Voron printer configuration lives in `config/`.

Repository layout:

```text
config/   Live Klipper/Moonraker config payload copied to the Voron
extras/   Reference files only: G-code, logs, pictures, docs, helper projects
```

To install on the printer, clone this repository and run:

```bash
cd /tmp
git clone git@github.com:Batcandoionline/All-Config-Voron.git
cd All-Config-Voron
bash config/scripts/install.sh
```

To update later from the printer:

```bash
cd ~/printer_data/config
bash scripts/update.sh
sudo systemctl restart moonraker
sudo systemctl restart klipper
```

Do not copy the repository root directly into `~/printer_data/config`.
The install/update scripts copy only `config/`; `extras/` is kept in GitHub for reference.
