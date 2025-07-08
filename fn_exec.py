###fn_execu.py

from tools import FunctionHandler  
import json
import time
import re
import os
import sys
import concurrent.futures
from typing import Dict, Any, Union, List, Optional

# Ensure path to Brain module is set correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from brain import GptAgent


def execute_function(function_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Executes a single function with error handling."""
    result = {
        'function': function_name,
        'parameters': parameters,
        'job_description': "",
        'execution_time': 0.0,
        'result': False,
        'response': "",
    }

    handler = FunctionHandler()
    if function_name not in handler.function_registry:
        result['error'] = f"Function '{function_name}' not found"
        return result

    func_info = handler.function_registry[function_name]
    schema = func_info.get('schema', {})
    required_params = schema.get('required', [])

    # Validate required parameters
    missing_params = [p for p in required_params if p not in parameters]
    if missing_params:
        result['error'] = f"Missing parameters: {', '.join(missing_params)}"
        result['missing_params'] = missing_params
        return result

    try:
        start_time = time.time()
        output = func_info['function'](**parameters)
        execution_time = time.time() - start_time

        result.update({
            'job_description': schema.get('description', ''),
            'execution_time': round(execution_time, 2),
            'result': bool(output),
            'response': str(output)
        })

    except Exception as e:
        result.update({
            'error': str(e),
            'response': f"Error: {str(e)}"
        })

    return result

def parse_function_response(response_text: str) -> Union[List[Dict], None]:
    """Extracts JSON array from AI response with multiple commands."""
    try:
        parsed = json.loads(response_text)
        if isinstance(parsed, list):
            return parsed
        return [parsed]
    except json.JSONDecodeError:
        pass

    # Try parsing codeblock
    json_match = re.search(r'```json\n?(\[.*?\])\n?```', response_text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except Exception:
            pass

    array_match = re.search(r'\[\s*\{.*\}\s*\]', response_text, re.DOTALL)
    if array_match:
        try:
            return json.loads(array_match.group())
        except Exception:
            pass

    return None

def execute_sequential_functions(function_calls: List[Dict]) -> List[Dict]:
    """Executes multiple functions one after another sequentially."""
    results = []

    for call in function_calls:
        try:
            res = execute_function(call['function'], call.get('parameters', {}))
            results.append(res)

            # If a function fails, you can break here if needed:
            # if not res.get('result', False):
            #     break

        except Exception as e:
            results.append({
                'function': call.get('function', 'unknown'),
                'parameters': call.get('parameters', {}),
                'error': str(e)
            })

    return results



def functioncall(user_input: str) -> List[Dict]:
    """Processes user input, executes commands in parallel, and provides post-execution feedback."""
    try:
        # Step 1: Ask Brain for function calls
        response = GptAgent().generate(user_input)
        response_text = response[0] if isinstance(response, tuple) else response

        function_calls = parse_function_response(response_text)

        # Step 2: If there are function calls, execute them
        if function_calls:
            print(f"🔄 Executing {len(function_calls)} parallel commands:")
            start_time = time.time()
            results = execute_sequential_functions(function_calls)
            total_time = round(time.time() - start_time, 2)
            #print('raw result', results)

            feedback = GptAgent().generate(f"""Give response based on the task execution results in less tokens as if you're reporting back to the user in natural language:\n\n{json.dumps(results, indent=2)}. Don't mention execution time""")

            # Append feedback as assistant_response
            results.append({
                'function': 'assistant_response',
                'response': feedback,
                'execution_time': total_time,
                'result': True
            })
            return results

        # Step 4: No function calls detected, return plain response
        #print(response_text)
        return [{
            'function': 'assistant_response',
            'response': response_text,
            'execution_time': 0.0,
            'result': True
        }]

    except Exception as e:
        return [{'error': f"System error: {str(e)}"}]


if __name__ == "__main__":
    while True:
        user_input = input('>>> ')
        output = functioncall(user_input)
        #print(json.dumps(output, indent=2))