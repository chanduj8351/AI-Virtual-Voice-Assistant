import requests
import json
import base64
import time
import re
import os


# API endpoint
API_URL = "https://api.zoo.dev/ai/text-to-cad/gltf"
AUTH_TOKEN = "Bearer ses-c5b5235f-ed10-4b8c-a719-5f32bec7de59"

# Headers
HEADERS = {
    "accept": "*/*",
    "authorization": AUTH_TOKEN,
    "content-type": "application/json",
    "origin": "https://text-to-cad.zoo.dev",
    "referer": "https://text-to-cad.zoo.dev/",
    "user-agent": ""
}
filepath = ""

def sanitize_filename(prompt):
    """Converts a text prompt into a safe filename (e.g., 'Flat Plate'mic → 'flat_plate.gltf')."""
    filename = re.sub(r'[^a-zA-Z0-9]', '_',prompt.lower().strip()) 
    filename = filename.replace('create_a_', '').strip()
    return f"{filename}.gltf"

def create_cad(prompt: str):
    """Send a request to generate a CAD model from text."""
    response = requests.post(API_URL, headers=HEADERS, json={"prompt": prompt})

    if response.status_code == 201:
        response_data = response.json()
        job_id = response_data.get("id")
        if job_id:
            print(f"✅ Job submitted! Job ID: {job_id}")
            return job_id
    else:
        print(f"❌ Request failed! Status Code: {response.status_code}")
        print(response.text)
        return None

def wait_for_completion(job_id: str):
    """Waits for the CAD process to complete and retrieves the result."""
    status_url = f"https://api.zoo.dev/user/text-to-cad/{job_id}"
    
    while True:
        response = requests.get(status_url, headers=HEADERS)

        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "unknown")

            if status == "completed":
                print("✅ CAD generation completed!")
                return data
            elif status in ["failed", "error"]:
                print(f"❌ CAD generation failed! Status: {status}")
                return None
            else:
                print(f"⏳ Processing... Status: {status}. Retrying in 5 seconds...")
                time.sleep(5)
        else:
            print(f"⚠️ Error fetching job status. Status Code: {response.status_code}")
            return None

def save_gltf_file(response_data, prompt):
    """Extracts the GLTF file from the response and saves it with a prompt-based name."""
    if "outputs" not in response_data:
        print("❌ No outputs found in response!")
        return None
    
    gltf_base64 = response_data["outputs"].get("source.gltf")
    if not gltf_base64:
        print("❌ No GLTF data found!")
        return None

    # Fix Base64 padding if necessary
    missing_padding = len(gltf_base64) % 4
    if missing_padding:
        gltf_base64 += "=" * (4 - missing_padding)

    try:
        gltf_data = base64.b64decode(gltf_base64)
        filename = sanitize_filename(prompt)

        filepath = os.path.join(os.getcwd(), "data", "cad", filename)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)  # Make sure folder exists

        with open(filepath, "wb") as f:
            f.write(gltf_data)

        return filepath

    except Exception as e:
        print(f"❌ Error decoding GLTF data: {e}")
        return None


def cad_design(prompt: str) -> str:
    job_id = create_cad(prompt)
    if job_id:
        response_data = wait_for_completion(job_id)
        if response_data:
            with open(os.path.join(os.getcwd(), "func", "assets", "cad_response.json"), "w") as f:
                json.dump(response_data, f, indent=4)

            filepath = save_gltf_file(response_data, prompt)
            return f"✅ File saved at: {filepath}" if filepath else "❌ Failed to save file."
    
    return "❌ CAD generation failed or file not saved."


if __name__ == "__main__":
    x = cad_design('a 1mm bolt')
    print(x)
























































# import requests
# import json
# import base64
# import time

# # API endpoint
# API_URL = "https://api.zoo.dev/ai/text-to-cad/gltf"
# AUTH_TOKEN = "Bearer ses-2c92e5ad-b0a0-4b87-ab79-f97fd3d2db66"

# # Headers
# HEADERS = {
#     "accept": "*/*",
#     "authorization": AUTH_TOKEN,
#     "content-type": "application/json",
#     "origin": "https://text-to-cad.zoo.dev",
#     "referer": "https://text-to-cad.zoo.dev/",
#     "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
# }



# def create_cad(prompt: str):
#     """Send a request to generate a CAD model from text."""
#     response = requests.post(API_URL, headers=HEADERS, json={"prompt": prompt})

#     if response.status_code == 201:
#         response_data = response.json()
#         job_id = response_data.get("id")
#         if job_id:
#             print(f"✅ Job submitted! Job ID: {job_id}")
#             return job_id
#     else:
#         print(f"❌ Request failed! Status Code: {response.status_code}")
#         print(response.text)
#         return None

# def wait_for_completion(job_id: str):
#     """Waits for the CAD process to complete and retrieves the result."""
#     status_url = f"https://api.zoo.dev/user/text-to-cad/{job_id}"
    
#     while True:
#         response = requests.get(status_url, headers=HEADERS)

#         if response.status_code == 200:
#             data = response.json()
#             status = data.get("status", "unknown")

#             if status == "completed":
#                 print("✅ CAD generation completed!")
#                 return data
#             elif status in ["failed", "error"]:
#                 print(f"❌ CAD generation failed! Status: {status}")
#                 return None
#             else:
#                 print(f"⏳ Processing... Status: {status}. Retrying in 5 seconds...")
#                 time.sleep(5)
#         else:
#             print(f"⚠️ Error fetching job status. Status Code: {response.status_code}")
#             return None

# def save_gltf_file(response_data):
#     """Extracts the GLTF file from the response and saves it."""
#     if "outputs" not in response_data:
#         print("❌ No outputs found in response!")
#         return
    
#     gltf_base64 = response_data["outputs"].get("source.gltf")
#     if not gltf_base64:
#         print("❌ No GLTF data found!")
#         return

#     # Fix Base64 padding if necessary
#     missing_padding = len(gltf_base64) % 4
#     if missing_padding:
#         gltf_base64 += "=" * (4 - missing_padding)

#     try:
#         gltf_data = base64.b64decode(gltf_base64)
#         file_name = prompt
#         with open("wing.gltf", "wb") as f:
#             f.write(gltf_data)
#         print("✅ GLTF file saved as 'output_model.gltf'")
#     except Exception as e:
#         print(f"❌ Error decoding GLTF data: {e}")

# def main():
#     prompt = "Create a top spring of an aircraft"

#     job_id = create_cad(prompt)
#     if job_id:
#         response_data = wait_for_completion(job_id)
#         if response_data:
#             # Save JSON response
#             with open("response.json", "w") as f:
#                 json.dump(response_data, f, indent=4)

#             # Save GLTF file
#             save_gltf_file(response_data)

# if __name__ == "__main__":
#     main()




























































# import requests
# import json
# from time import sleep


# def cad():
#     # API endpoint
#     url = "https://api.zoo.dev/ai/text-to-cad/gltf"


#     # Headers
#     headers = {
#         "accept": "*/*",
#         "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
#         "authorization": "Bearer ses-2c92e5ad-b0a0-4b87-ab79-f97fd3d2db66",
#         "content-type": "application/json",
#         "origin": "https://text-to-cad.zoo.dev",
#         "referer": "https://text-to-cad.zoo.dev/",
#         "sec-fetch-mode": "cors",
#         "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
#     }

#     # Request payload
#     data = {"prompt": ""}

#     # Send the request
#     response = requests.post(url, headers=headers, json=data)

#     # Check response status
#     if response.status_code == 201:
#         print("✅ First request successful!")

#         # Extract job ID from response
#         response_data = response.json()
#         job_id = response_data.get("id")  # Ensure the response contains 'id'

#         if job_id:
#             print(f"🔄 Processing Job ID: {job_id}")

#             # Second API call to check job status
#             status_url = f"https://api.zoo.dev/user/text-to-cad/{job_id}"

#             # Headers for second request
#             headers["method"] = "GET"

#             response = requests.get(status_url, headers=headers)

#             if response.status_code == 200:
#                 print("✅ Second request successful! Here is the response:")
#                 #print(json.dumps(response.json(), indent=4))
                
#                 # Optionally, save the response
#                 with open("response.json", "w") as f:
#                     json.dump(response.json(), f, indent=4)

#             else:
#                 print(f"⚠️ Error fetching job status. Status Code: {response.status_code}")
#         else:
#             print("❌ Error: Job ID not found in response.")
#     else:
#         print(f"❌ First request failed! Status Code: {response.status_code}")
#         print(response.text)  # Print error details if any






# import json
# import base64

# # Load the JSON response from the file
# with open("response.json", "r") as f:
#     data = json.load(f)

# # Extract the GLTF base64 data
# gltf_base64 = data["outputs"]["source.gltf"]

# # Fix padding issue by adding "=" manually
# missing_padding = len(gltf_base64) % 4
# if missing_padding:
#     gltf_base64 += "=" * (4 - missing_padding)

# # Decode the base64 data
# try:
#     gltf_data = base64.b64decode(gltf_base64)
    
#     # Save the decoded data as a .gltf file
#     with open("output_model.gltf", "wb") as f:
#         f.write(gltf_data)

#     print("✅ GLTF file saved as 'output_model.gltf'")
# except Exception as e:
#     print(f"❌ Error decoding Base64: {e}")
