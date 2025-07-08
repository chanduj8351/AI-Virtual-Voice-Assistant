import requests
import re
import json
import fitz  # PyMuPDF

def Phind(prompt: dict, system_prompt: str, model: str = "Phind-405B", stream_chunk_size: int = 12, stream: bool = True) -> str:
    headers = {"User-Agent": ""}
    prompt.insert(0, {"content": system_prompt, "role": "system"})
    payload = {
        "additional_extension_context": "",
        "allow_magic_buttons": True,
        "is_vscode_extension": True,
        "message_history": prompt,
        "requested_model": model,
        "user_input": prompt[-1]["content"],
    }

    chat_endpoint = "https://https.extension.phind.com/agent/"
    response = requests.post(chat_endpoint, headers=headers, json=payload, stream=True)

    streaming_text = ""
    for value in response.iter_lines(decode_unicode=True, chunk_size=stream_chunk_size):
        modified_value = re.sub("data:", "", value)
        if modified_value:
            json_modified_value = json.loads(modified_value)
            try:
                if stream:
                    streaming_text += json_modified_value["choices"][0]["delta"]["content"]
            except:
                continue

    return streaming_text

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file."""
    try:
        doc = fitz.open(pdf_path)
        text = "\n".join(page.get_text() for page in doc)
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

def pdf_analyzer(pdf_path: str, prompt) -> str:
    """Summarize the extracted text from a PDF using Phind."""
    pdf_text = extract_text_from_pdf(pdf_path)
    if "Error reading PDF" in pdf_text:
        return pdf_text

    prompt = [{"role": "user", "content": f"{prompt}: {pdf_text}"}]  # Limit text to 5000 chars[:100000]
    summary = Phind(prompt, "Be Helpful and Friendly")
    return summary

if __name__ == "__main__":
    pdf_path = input("Enter PDF file path: ")
    prompt = input("Enter prompt: ")
    summary = pdf_analyzer(pdf_path, prompt)
    print("\nSummary:\n", summary)
