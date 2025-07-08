import threading
from openai import OpenAI
from dotenv import load_dotenv
import cv2
import os
import google.generativeai as ai
import PIL.Image
from absl import logging
import grpc._channel
logging.set_verbosity(logging.INFO)
import grpc
grpc._channel._Rendezvous.__del__ = lambda *args, **kwargs: None
import threading
print([t.name for t in threading.enumerate()])


load_dotenv()
ai.configure(api_key=os.environ["GEMINI_API_KEY"])

def image_capture(image_path: str=os.getcwd() + "\\temp\\img\\cap_img.png") -> str:
    print("\033[92m" + "Turned on Realtime Vision. Capturing Image.\033[0m")
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cv2.imwrite(image_path, frame)
    print("📷 " + "Image captured...")

    cap.release() 
    cv2.destroyAllWindows() 
    return image_path


def cam_vision(image_path, prompt: dict, model_name = "gemini-1.5-flash-002"):
    
    try:
        model = ai.GenerativeModel(model_name)
        response = model.generate_content([prompt, PIL.Image.open(image_path)])
        return response.text
    
    except Exception as e:
        print("\033[91m" + f"Error occurred: {e}\033[0m")
        return ""
    finally:
        pass


def online_img_vision_search(prompt: str, image_url: str) -> str:
        client = OpenAI(
            api_key=os.environ["G4F_API_KEY"],
            base_url="https://api.a4f.co/v1"
        )
        response = client.chat.completions.create(
            model="provider-5/gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url  # image address
                            }
                        }
                    ]
                }
            ]
        )
        return response.choices[0].message.content


        
if __name__ == '__main__':
    image = image_capture()
    #x = online_img_vision_search(prompt = "what do you observe", image_url = image)
    x = cam_vision(image_path=image,prompt = "what do you observe")
    print(x)


