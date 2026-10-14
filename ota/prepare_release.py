#!/usr/bin/env python3
"""Stage a verified XiaoZhi app binary and enable its GitHub Pages OTA manifest."""
import argparse
import json
import re
import struct
from pathlib import Path

BOARD = "sp-esp32-s3-1.28-cam-low"
ORIGIN = "https://vdlaptrinh.github.io/esp_web_flasher"


def inspect_firmware(path):
    data = path.read_bytes()
    if len(data) < 112 or data[0] != 0xE9 or struct.unpack_from("<I", data, 32)[0] != 0xABCD5432:
        raise ValueError("Use build/xiaozhi.bin, not merged-binary.bin")
    if len(data) > 0x3F0000:
        raise ValueError("Firmware exceeds the board OTA partition size")
    version = data[48:80].split(b"\0", 1)[0].decode("ascii")
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)+", version):
        raise ValueError("Firmware version must use numeric dotted segments")
    config = json.loads((path.parent / "config/sdkconfig.json").read_text())
    if config.get("IDF_TARGET") != "esp32s3" or not config.get("BOARD_TYPE_SP_ESP32_S3_128_CAM_LOW"):
        raise ValueError("Build configuration does not match the OTA board")
    if not config.get("XIAOZHI_CUSTOM_FIRMWARE_OTA"):
        raise ValueError("Build does not include the custom firmware OTA channel; rebuild first")
    return data, version


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("firmware", type=Path)
    args = parser.parse_args()
    data, version = inspect_firmware(args.firmware.resolve())
    root = Path(__file__).resolve().parent.parent
    destination = root / "firmware" / ("xiaozhi-" + version + ".bin")
    destination.parent.mkdir(exist_ok=True)
    if destination.exists() and destination.read_bytes() != data:
        raise ValueError("Version already exists with different firmware; increase PROJECT_VER")
    destination.write_bytes(data)
    manifest = root / "ota" / (BOARD + ".json")
    content = {"board": BOARD, "version": version,
               "url": ORIGIN + "/firmware/" + destination.name, "enabled": True}
    temporary = manifest.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(content, indent=2) + "\n")
    temporary.replace(manifest)
    print("Firmware:", destination)
    print("Manifest:", manifest)
    print("Commit/push both files, wait for GitHub Pages deployment, then verify both URLs.")


if __name__ == "__main__":
    main()
