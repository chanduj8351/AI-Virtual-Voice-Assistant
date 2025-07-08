from func.openapps import AppWebsiteOpener
from auto.erp import Erp
from auto.whatsapp import WhatsApp
from func.closeapps import CloseApps
from auto.mobile import AndroidDevice
from func.app_status import AppInfo
from func.internet import Internet
from func.system import *
from func.file_manager import FileManager
import json
import os

with open(os.getcwd() + "/assets/json/extensions.json", 'r') as f:
    extensions = json.load(f)

class FunctionHandler:
    def __init__(self):
        self.erp = Erp()
        self.whatsapp = WhatsApp()
        self.android_device = AndroidDevice()
        
        self.function_registry = {
            "open_main": {
                'function': AppWebsiteOpener.open_main,
                'schema': {
                    'name': 'open_main',
                    'description': 'Opens applications or websites',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'app_name': {'type': 'string', 'description': 'Name of application/website to open'}
                        },
                        'required': ['app_name']
                    }
                }
            },
            "close_app": {
                "function": CloseApps.close_app,
                'schema': {
                    "name": "close_app",
                    "description": "Closes a specific application if it's running",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Name of the application to close"}
                        },
                        "required": ["app_name"]
                    }
                }
            },
            "mobile_device_connection": {
                "function": self.android_device.connect_device,
                'schema': {
                    "name": "mobile_device_connection",
                    "description": "Connects to the mobile device",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            "mobile_device_disconnection": {
                "function": self.android_device.disconnect_device,
                'schema': {
                    "name": "mobile_device_disconnection",
                    "description": "Disconnects from the mobile device",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            "mobile_device_battery_status": {
                "function": self.android_device.get_battery_status,
                'schema': {
                    "name": "mobile_device_battery_status",
                    "description": "Gets the battery status of the mobile device",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            "mobile_device_unlock": {
                "function": self.android_device.unlock_device,
                'schema': {
                    "name": "mobile_device_unlock",
                    "description": "Unlocks the mobile device",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            "mobile_device_send_text": {
                "function": self.android_device.send_text,
                'schema': {
                    "name": "mobile_device_send_text",
                    "description": "Sends text to the mobile device",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "Text to send"}
                        },
                        "required": ["text"]
                    }
                }
            },
            "mobile_device_make_call": {
                "function": self.android_device.make_call,
                'schema': {
                    "name": "mobile_device_make_call",
                    "description": "Makes a phone call from the mobile device",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "phone_number": {"type": "string", "description": "Phone number to call"}
                        },
                        "required": ["phone_number"]
                    }
                }
            },
            "is_app_running": {
                "function": AppInfo.is_app_running,
                'schema': {
                    "name": "is_app_running",
                    "description": "Checks if a specific application is running. [Condition/Rule: Cross check for app status, If the app is running or not in the background]. Example: If the user asks did you open notepad? Action: is_app_running('notepad'). Based on the results the other tool functions may responds.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "app_name": {"type": "string", "description": "Name of the application to check"}
                        },
                        "required": ["app_name"]
                    }
                }
            },
            "get_active_window_info": {
                "function": AppInfo.get_active_window_info,
                'schema': {
                    "name": "get_active_window_info",
                    "description": "Gets the title and process name of the currently active window of the PC/your system",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            "get_active_app_name": {
                "function": AppInfo.get_app_name,
                'schema': {
                    "name": "get_active_app_name",
                    "description": "Extracts the app name from the active window title [returns the active app name which is running on the screen.]",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            "app_status_check": {
                "function": AppInfo.app_status_check,
                'schema': {
                    "name": "app_status_check",
                    "description": "Continuously prints active window info for a given duration in seconds.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "duration": {"type": "number", "description": "Duration in seconds [set to default to 10 seconds]"}
                        },
                        "required": ["duration"]
                    }
                }
            },
            "is_connected": {
                "function": Internet.is_connected,
                'schema': {
                    "name": "is_connected",
                    "description": "Check if the device[PC] is connected to the internet. [This tool used for check for the internet connection (cross check function)]",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            "connect_to_wifi": {
                "function": Internet.connect_to_wifi,
                'schema': {
                    "name": "connect_to_wifi",
                    "description": "Connects to a specified Wi-Fi network.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ssid": {"type": "string", "description": "The SSID of the Wi-Fi network [set to default to 'Hello']"},
                            "password": {"type": "string", "description": "The password of the Wi-Fi network [set to default to '12345678']"}
                        },
                        "required": ["ssid", "password"]
                    }
                }
            },
            "disconnect_wifi": {
                "function": Internet.disconnect_wifi,
                'schema': {
                    "name": "disconnect_wifi",
                    "description": "Disconnects from the current Wi-Fi network.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            "check_internet_speed": {
                "function": Internet.check_internet_speed,
                'schema': {
                    "name": "check_internet_speed",
                    "description": "Checks the internet speed of the PC (download, upload, and ping).",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            "get_current_network": {
                "function": Internet.get_current_network,
                'schema': {
                    "name": "get_current_network",
                    "description": "Retrieves the currently connected Wi-Fi network.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            "pc_battery_info":{
                "function": battery_info,
                'schema': {
                    "name": "pc_battery_info",
                    "description": "Retrieves/Gets the battery information of the PC.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            "get_brightness_level":{
                "function": ScreenBrightnessControl().get_brightness_level,
                'schema': {
                    "name": "get_brightness_level",
                    "description": "Retrieves/Gets the brightness level of the PC.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            "set_brightness":{
                "function": ScreenBrightnessControl().set_brightness,
                'schema': {
                    "name": "set_brightness_level",
                    "description": "Sets the brightness level of the PC. [Increase/decrease in the brightness level by 20%]",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "level": {"type": "number", "description": "The brightness level to set [check the get brightness level function first to get the current brightness level. And then increase by 20. The level should be int only. Set the level as you want by (20%) increase or decrease]"}
                        },
                        "required": ["level"]
                    }
                }
            },
            "cpu_usage":{
                "function": cpu_usage,
                'schema': {
                    "name": "cpu_usage",
                    "description": "Retrieves/Gets the CPU usage of the PC.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            "window_maximize":{
                "function": system_actions.max_window,
                'schema': {
                    "name": "window_maximize",
                    "description": "Maximizes the window of the PC.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            "window_minimize":{
                "function": system_actions.min_window,
                'schema': {
                    "name": "window_minimize",
                    "description": "Minimizes the window of the PC.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            "switch_to_recent_window":{
                "function": system_actions.switch_to_recent_window,
                'schema': {
                    "name": "switch_to_recent_window",
                    "description": "Switches to the recent window of the PC.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            "write":{
                "function": system_actions.write,
                'schema': {
                    "name": "write",
                    "description": "Writes text on the PC.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "The text to write"}
                        },
                        "required": ["text"]
                    }
                }
            },
            "pc_screenshot": {
                "function": system_actions.pc_screenshot,
                'schema': {
                    "name": "pc_screenshot",
                    "description": "Takes a screenshot of the PC.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            "refresh_home_screen": {
                "function": system_actions.refresh_home_screen,
                'schema': {
                    "name": "refresh_home_screen",
                    "description": "Refreshes the home screen of the PC.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            "write_to_file": {
                "function": system_actions.write_to_file,
                'schema': {
                    "name": "write_to_file",
                    "description": "Writes text to a file.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "The path of the file to write the content"},
                            "content": {"type": "string", "description": "The content to write to the file"}
                        },
                        "required": ["file_path", "content"]
                    }
                }
            }
        }
