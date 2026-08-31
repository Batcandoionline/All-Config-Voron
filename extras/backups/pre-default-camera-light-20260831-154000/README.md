# Backup before removing WS2812B lighting assumption

- Date: 2026-08-31
- Artifact: `config/scripts/patches/ktamv-center-highlight-fallback.patch`
- SHA256 before edit: `df35b463c9acb07097fb3f6349ce7a72331a932b5eb5be3b8526543b4154494b`
- Reason: preserve the detector patch before changing comments/documentation to
  state that camera-supplied illumination is the optical input and the external
  ESP32/WS2812B ring is not required or controlled.
- The live detector source backup is at
  `/home/voron/printer_data/config_backups/pre-default-camera-light-20260831-154000/runtime/ktamv_server_dm.py`.
