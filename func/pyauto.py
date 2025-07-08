import pyautogui
from time import sleep
import pyperclip
import os
import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.vision import cam_vision

def execute_hotkey(*hotkeys):
    try:
        if not all(isinstance(key, str) for key in hotkeys):
            raise ValueError("All hotkeys must be strings.")
        
        pyautogui.hotkey(*hotkeys)
        print(f"Successfully executed hotkey(s): {', '.join(hotkeys)}")
    
    except pyautogui.FailSafeException:
        print("Hotkey execution interrupted. Check your keyboard or cursor position.")
    except ValueError as e:
        print(f"Input error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def copy_text(text, img_path=os.getcwd()+"\\temp\\img\\copy.png"):
    """
    Function to copy the given text to the clipboard.
    """
    try:
        pyautogui.screenshot(imageFilename=img_path)
        sleep(1)
        x = cam_vision(image_path=img_path, prompt=text)
        pyperclip.copy(x)
        print(f"Text copied successfully to clipboard:.{x}")
        

    except Exception as e:
        print(f"An error occurred while copying text: {e}")

        

if __name__ == "__main__":
    copy_text("Return text from 'Have You Ever' to 'Laptops'") 

