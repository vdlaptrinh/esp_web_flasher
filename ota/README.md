# Custom firmware OTA — sp-esp32-s3-1.28-cam-low

Manifest: https://vdlaptrinh.github.io/esp_web_flasher/ota/sp-esp32-s3-1.28-cam-low.json

The ESP32 uses GET to check this manifest after receiving chatbot configuration
from Tenclass. Only a matching board and a newer numeric version can update.
`enabled: false` disables the release. HTTP/JSON failures leave startup working.

## First installation

The firmware source PROJECT_VER is now 2.5.1. Activate ESP-IDF 6.1, confirm the
selected board, build and flash the first custom-channel firmware over USB:

```sh
cd /Users/dailuu/Documents/esp32_projects/xiaozhi-esp32
idf.py build
idf.py flash monitor
```

Do not upload the older build/xiaozhi.bin left from before this change.
Firmware must fit the 0x3f0000-byte OTA slot. Use the app binary, not merge-bin.

## Prepare a release

For each subsequent release, increase PROJECT_VER, build again, then run:

```sh
cd /Users/dailuu/Documents/githubvd/esp_web_flasher
python3 ota/prepare_release.py /Users/dailuu/Documents/esp32_projects/xiaozhi-esp32/build/xiaozhi.bin
```

The script checks the embedded version, OTA slot size, ESP32-S3 board selection
and custom-channel flag. It copies the binary into firmware/ and enables the
manifest. A published version must not be replaced with different bytes.

Commit/push the generated JSON and binary together. Enable GitHub Pages from
this repository's main branch/root. After deployment, open both public URLs;
the JSON must return the release metadata and the .bin URL must download the app.
Reboot the bot to check the new version. The already installed 2.5.1 does not
reinstall the same version. Use 2.5.2 or greater for the next update.

The initial manifest remains disabled until a verified new build is staged.
Manual self.upgrade_firmware remains available. Assets and partition layout
are not changed by firmware OTA; updates must preserve the installed layout.
