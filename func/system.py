import winreg
from difflib import get_close_matches
import os
import pyautogui
import psutil
from datetime import datetime
from time import sleep
import screen_brightness_control as sbc


# -------------------------------------BATTERY--------------------------------------------
def battery_info():
    try:
        battery = psutil.sensors_battery()
        percentage = battery.percent
        charging = battery.power_plugged
        print(f"Percentage:{percentage}% | Charging:{charging}")
        return percentage, charging
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None


# -------------------------------------BRIGHTNESS--------------------------------------------
class ScreenBrightnessControl:
    def __init__(self):
        self.current_brightness = sbc.get_brightness()

    def get_brightness_level(self):
        return self.current_brightness

    def set_brightness(self, level):
        if 0 <= level <= 100:
            sbc.set_brightness(level)
            self.current_brightness = sbc.get_brightness()  # Update the current brightness
            return True
        else:
            return False
            #raise ValueError("Brightness level must be between 0 and 100")
        

    # def brightness(self, new_level: int=None) -> bool:
    #     brightness = self.get_brightness()
    #     print(f"Current brightness level: {brightness[0]}%")

    #     if new_level is not None:
    #         try:
    #             self.set_brightness(new_level)
    #             return f"Brightness level set to: {new_level}%"
    #         except ValueError as e:
    #             print(e)
    #             return False
    #         return True
        


# -------------------------------------CPU USAGE--------------------------------------------

def cpu_usage(bars: int=50, sleep_time:int=0.5):
    
    while True:
        cpu_usage=psutil.cpu_percent(interval=1)
        cpu_percent=cpu_usage/100.0
        cpu_bar= "█" * int(cpu_percent*bars) + '-' * (bars-int(cpu_percent*bars)) 
        
        memory_usage=psutil.virtual_memory().percent
        memory_percent=memory_usage/100.0
        memory_bar= "█" * int(memory_percent*bars) + '-' * (bars-int(memory_percent*bars))

        usage_info = {'CPU_USAGE': {"BAR": cpu_bar, "PERCENT": cpu_usage}, "MEMORY_USAGE": {"BAR": memory_bar, "PERCENT": memory_usage}}

        # print(f"\rCPU USAGE: |{cpu_bar}| {cpu_usage:.2f}% ", end="")
        # print(f"MEMORY USAGE: |{memory_bar}| {memory_usage:.2f}%", end="\r")
        sleep(sleep_time)
        return usage_info

# -------------------------------------SYSTEM INFO--------------------------------------------
def sys_info():
    system_info = {}

    print('Sytem Information:')
    
    # cpu information
    cpu_count_logic=psutil.cpu_count(logical=True)
    cpu_count_physical=psutil.cpu_count(logical=False)
    cpu_frequency=psutil.cpu_freq(percpu=False)
    cpu_percent=psutil.cpu_percent(interval=1, percpu=False)

    system_info["CPU_INFORMATIO"] = {"Logical_CPUs": cpu_count_logic, "Physical_CPUs": cpu_count_physical, "CPU_Frequency": cpu_frequency, "CPU_Usage": cpu_percent}

    print(f"Logical CPUs: {cpu_count_logic}")
    print(f"Physical CPUs: {cpu_count_physical}")
    print(f"CPU Frequency: {cpu_frequency.current} MHz")
    print(f"CPU Usage: {cpu_percent}%")
    print("-" * 100)
    
    # memory information
    virtual_memory=psutil.virtual_memory()
    swap_memory=psutil.swap_memory()

    system_info["MEMORY_INFORMATION"] = {"Total_Virtual_Memory": virtual_memory.total / (1024 ** 3), "Used_Virtual_Memory": virtual_memory.used / (1024 ** 3), "Total_Swap_Memory": virtual_memory.total / (1024 ** 3), "Used_Swap_Memory": virtual_memory.used / (1024 ** 3)}

    print(f"\nMemory Information:")
    print(f"Total Virtual Memory: {virtual_memory.total / (1024 ** 3)} GB")
    print(f"Used Virtual Memory: {virtual_memory.used / (1024 ** 3)} GB")
    print(f"Total Swap Memory: {virtual_memory.total / (1024 ** 3)} GB")
    print(f"Used Swap Memory: {virtual_memory.used / (1024 ** 3)} GB")
    print("-" * 100)

    disk_partitions = psutil.disk_partitions(all=False)
    disk_usage = psutil.disk_usage(disk_partitions[0].device)
    disk_io_counters = psutil.disk_io_counters(perdisk=False)

    system_info["DISK_INFORMATION"] = {"Disk_partitions": disk_partitions, "Disk_usage": disk_usage, "Disk_io_counters": disk_io_counters}

    print(f"\nDisk Information:")
    print(f"Disk Partitions: {disk_partitions}")
    print(f"Disk Usage: {disk_usage.percent}%")
    print(f"Disk IO Counters: {disk_io_counters}")
    print("-" * 100)

    ## Network Information
    net_io_counters = psutil.net_io_counters(pernic=False)
    net_connections = psutil.net_connections(kind='inet')
    net_if_address = psutil.net_if_addrs()
    #net_stat = psutil.net_stat()

    system_info["NETWORK_INFORMATION"] = {"Network_IO_Counters": net_io_counters, "Network_Connections": net_connections, "Network_IF_Address": net_if_address}

    # print(f"\nNetwork Information:")
    # print(f"Network IO Counters: {net_io_counters}")
    # print(f"Network Connections: {net_connections}")
    # print(f"Network IF Address: {net_if_address}")
    # print("-" * 100)


    ### System BootTime
    boot_time = psutil.boot_time()
    boot_time = datetime.fromtimestamp(boot_time)
    formatted_boot_time = boot_time.strftime("%Y-%m-%d %H:%M:%S UTC")

    system_info["SYSTEM_BOOT_TIME"] = formatted_boot_time
    print(f"\nSystem Boot Time: {formatted_boot_time}")
    print("-" * 100)
    
    
    ### Connected Users
    users = psutil.users()
    
    system_info["CONNECTED_USERS"] = users
    print(f"\nConnected Users:{users}")
    print("-" * 100)


    ### PROCESS INFORMATION
    processes = list(psutil.process_iter())
    system_info["PROCESS_INFORMATION"] = {"Number of Processes": len(processes), "Processes Ids":[process.pid for process in processes]} 

    print(f"\nProcess Information:")
    print(f"Number of Processes: {len(processes)}")
    print(f"Process Ids: {[process.pid for process in processes]}")
    print("-" * 100)
    

    ### CPU Times
    cpu_times = psutil.cpu_times()
    system_info["CPU_TIMES"] = cpu_times
    print(f"\nCPU Times:{cpu_times}")
    print("-" * 100)
    
    return system_info

class system_actions():
    @staticmethod
    def max_window():
        try:
            pyautogui.hotkey("win", "up")
            return True
        except Exception as e:
            print(f"Window Maximation Failed!")
            return False
    @staticmethod
    def min_window():
        try:
            pyautogui.hotkey("win", "down")
            return True
        except Exception as e:
            print(f"Window Minimization Failed!")
            return False

    @staticmethod
    def cycle_through_open_windows():
        try:
            pyautogui.hotkey("alt", "esc")
        except Exception as e:
            print(f"Window Switching Failed!")
    @staticmethod
    def go_back():
        try:
            pyautogui.hotkey("alt", "left")
            return True
        except Exception as e:
            print(f"Going Back Failed!")
            return False
    @staticmethod
    def switch_to_recent_window():
        try:
            pyautogui.hotkey("alt", "tab")
            return True
        except Exception as e:
            print(f"Switching to Recent Window Failed!")
            return False
    @staticmethod
    def write(text):
        try:
            pyautogui.typewrite(text)

        except Exception as e:
            return f"Writing Failed!"
    @staticmethod
    def copy():
        try:
            pyautogui.hotkey("ctrl", "c")
            return True
        except Exception as e:
            print(f"Copying Failed!")
            return False
    @staticmethod
    def paste():
        try:
            pyautogui.hotkey("ctrl", "v")
        except Exception as e:
            print(f"Pasting Failed!")
    @staticmethod
    def pc_screenshot():
        try:
            screenshot_path = pyautogui.screenshot().save(f"{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.png")
            return f"Screenshot saved at: {screenshot_path}"
        except Exception as e:
            return f"Screenshot Failed!"
    @staticmethod
    def refresh_home_screen():
        try:
            pyautogui.hotkey('fn', 'f5')
        except Exception as e:
            print(f"Refreshing Home Screen Failed!")

    @staticmethod
    def is_app_installed(app_name):
        paths_to_check = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        ]
        installed_apps = []

        try:
            # Search in registry paths
            for path in paths_to_check:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                for i in range(0, winreg.QueryInfoKey(key)[0]):  # Iterate through subkeys
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)
                    try:
                        display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                        installed_apps.append(display_name)
                    except FileNotFoundError:
                        pass
                    finally:
                        winreg.CloseKey(subkey)
                winreg.CloseKey(key)

            # Find the closest match for the app name
            closest_matches = get_close_matches(app_name, installed_apps, n=1, cutoff=0.5)

            if closest_matches:
                return f"Found closest match: {closest_matches[0]}"
            else:
                return f"No match found for '{app_name}'."

        except Exception as e:
            print(f"Error: {e}")
            return f"An error occurred: {e}"
        
    @staticmethod
    def volume_control():
        try:
            pyautogui.press('volumeup')
        except Exception as e:
            print(f"Volume Up Failed!")

    @staticmethod
    def write(text: str) -> str:
        try:
            pyautogui.typewrite(text, interval=0.3)
            return True
        except Exception as e:
            print(f"Writing Failed!")
            return False
    @staticmethod
    def write_to_file(file_path: str, content: str) -> bool:
        try:
            with open(file_path, 'w') as file:
                file.write(content)
            return True
        except Exception as e:
            print(f"Writing to file failed: {e}")
            return False



