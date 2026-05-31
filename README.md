# All-Config-Voron

Main Voron printer configuration lives in `config/`.

To install on the printer, clone this repository and run:

```bash
cd /tmp
git clone https://github.com/Batcandoionline/All-Config-Voron.git
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

Do not copy the repository root directly into `~/printer_data/config`; the
root also contains backups, logs, G-code, and helper projects.
