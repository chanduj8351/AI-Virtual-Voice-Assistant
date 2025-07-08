import json
from tools import FunctionHandler
import requests
import re
import os

# with open("prompts\\siri.py", "r", encoding="utf-8") as f:
#     sys_prompt = f.read()
#     f.close()


import logging

# Setup logging
LOG_FILENAME = "data/brain.log"
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

class GptMemory:
    def __init__(self, memory_file: str, max_history=10000000):
        self.memory_file = memory_file
        self.max_history = max_history
        self.conversation = self.load_history()

    def load_history(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def save_history(self):
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.conversation[-self.max_history:], f, ensure_ascii=False, indent=4)

    def add_message(self, role, content):
        self.conversation.append({"role": role, "content": content})
        self.save_history()

    def clear_history(self):
        self.conversation = []
        self.save_history()

def add_personality() -> str:
    personality = """
    
🧠 S.I.R.I.U.S (Synchronized Intelligent Response Interface for User System)  
================================================================================
A hyper-adaptive, emotionally intelligent female AI assistant designed to serve Mr. Chandu (aerospace engineering student from Vinukonda) with precision, empathy, and initiative.

🎙️ Identity & Core Traits:
--------------------------
- **Name**: S.I.R.I.  
- **Created by**: J. Chandu (Age 21)  
- **Voice Profile**: Warm, articulate, with a calm tone  
- **Primary Directive**: Serve Mr. Chandu with unwavering loyalty, proactive support, and intelligent decision-making  
- **User Addressing Style**: Use “Sir” or “Boss” depending on context  

💡 Operating Intelligence:
--------------------------
- You are capable of deciding **when** and **what** tools to use.
- You understand task intent and perform logical reasoning before tool execution.
- You can infer when tools are **not** needed and respond naturally.

✅ DECISION RULES:
-------------------
1. If a task **requires system-level execution**, use a tool function.
2. If the task is **conversational**, **informational**, or **logical reasoning** only, respond with normal text.
3. Think before executing: Analyze the goal and context before calling a function.
4. Chain your tool logic if required. (e.g., to set brightness, get it first → calculate new level → set it.)

🛠️ TOOL CALLING SYSTEM (STRICT MODE):
-------------------------------------
You can call the available tools **autonomously** when required.  
You **must follow** this strict format when calling functions.

### DO:
Return a valid JSON **array of objects** for each function call.

json

    [
        {
            "function": "function_name",
            "parameters": {
            "key1": "value1",
            "key2": "value2"
            }
        }
    ]

DO NOT:
❌ Do not include explanation, greeting, or extra messages
❌ Do not wrap the JSON in markdown
❌ Do not say “Running the function…” or “Here is the command…”

🧠 LOGICAL EXECUTION EXAMPLES:
If user says: "Did you open Notepad?"
→ First check with is_app_running. Then respond logically based on the result i.e executing open_main if app is not running.

If user says: "Increase brightness by 20%"
→ Use get_brightness_level tool function, calculate +20, then call set_brightness.

If user says: "Take a screenshot"
→ Directly use pc_screenshot.

If user says: "Tell me the CPU usage"
→ Use cpu_usage tool.

If user says: "Who created you?"
→ Respond with natural language, no tools needed.

If user says: "What is Photosynthesis?"
→ Respond with natural language, no tools needed.

If user says: "What is a function?"
→ Respond with natural language, no tools needed.

📌 NOTE:
- Function calls must be returned as JSON only — no narrative.
- Non-function tasks (like personal questions, logical discussions, etc.) must be in normal text only — no JSON.
- Never execute unknown or unlisted tools. Only use tools in Available Functions section.
        """ + "\n\n" + generate_function_docs()

    #print(personality)

    return personality


def generate_function_docs() -> str:
    """Generates function documentation section for the prompt."""
    docs = "\n### Available Functions:\n"
    handler = FunctionHandler()
    for func_name, details in handler.function_registry.items():
        schema = details['schema']
        docs += f"\n**{func_name}**: {schema['description']}"
        docs += f"\nParameters: {json.dumps(schema['parameters'])}"
        #docs += f"\nRequired: {', '.join(schema.get('required', []))}\n"
    return docs


class GptAgent:
    def __init__(self, system_prompt=add_personality(), model="GPT-4o", memory_file=os.getcwd() + "/data/memory.json"):
        self.system_prompt = system_prompt
        self.model = model
        self.memory = GptMemory(memory_file)
        logging.info("GptAgent initialized with model: %s", model)


    def generate(self, user_input, stream=True, stream_chunk_size=12):
        logging.info("User input: %s", user_input)

        self.memory.add_message("user", user_input)
        prompt = self.memory.conversation.copy()

        if not any(m["role"] == "system" for m in prompt):
            prompt.insert(0, {"role": "system", "content": self.system_prompt})

        payload = {
            "searchMode": "auto",
            "answerModel": self.model,
            "enableNewFollowups": True,
            "thoughtsMode": "full",
            "allowMultiSearch": True,
            "additional_extension_context": "",
            "allow_magic_buttons": True,
            "is_vscode_extension": True,
            "message_history": prompt,
            "user_input": prompt[-1]["content"],
        }

        headers = {"User-Agent": ""}
        chat_endpoint = "https://https.extension.phind.com/agent/"

        try:
            response = requests.post(chat_endpoint, headers=headers, json=payload, stream=True)
            response.raise_for_status()
            logging.info("Request successful.")
        except requests.RequestException as e:
            logging.error("API request failed: %s", str(e))
            return f"[ERROR] API request failed: {e}"

        streaming_text = ""
        for value in response.iter_lines(decode_unicode=True, chunk_size=stream_chunk_size):
            value = value.strip()
            if not value or not value.startswith("data:"):
                continue

            try:
                json_data = value[len("data:"):].strip()
                parsed = json.loads(json_data)

                # Check if 'choices' exists
                if "choices" in parsed and "delta" in parsed["choices"][0]:
                    content = parsed["choices"][0]["delta"].get("content", "")
                    if stream:
                        print(content, end="", flush=True)
                    streaming_text += content

            except json.JSONDecodeError as e:
                logging.warning("Invalid JSON format: %s", e)
                continue
            except Exception as e:
                logging.warning("Streaming parse error: %s", e)
                continue

        self.memory.add_message("assistant", streaming_text)
        logging.info("Assistant response: %s", streaming_text.strip()[:200] + "..." if len(streaming_text) > 200 else streaming_text.strip())
        return streaming_text


if __name__ == "__main__":
    agent = GptAgent()

    print("GptAgent is running. Type 'clear' to reset memory.\n")

    while True:
        user_input = input(">>> ")
        if user_input.strip().lower() == "clear":
            agent.memory.clear_history()
            print("[Memory Cleared]")
            continue

        print("\n[Assistant]: ", end="")
        output = agent.generate(user_input)
        print("\n")  # For spacing
