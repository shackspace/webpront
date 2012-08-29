from helpers import scanserial
from settings import load_settings

settings = load_settings()

def build_device_list():
    device_settings = settings.core.printer.devices
    match_includes = len(device_settings.includes) > 0
    
    raw_devices = scanserial()
    device_dict = {}
    index = 0
    for device in raw_devices:
        if match_includes:
            if not device in device_settings.includes:
                continue
        if device in device_settings.excludes:
            continue
        device_dict[index] = device
        index = index + 1
    return device_dict

devices = build_device_list()

device_occupations = {}

sessions = {}