import ollama
import requests


def get_current_weather(city):
    base_url = f"https://wttr.in/{city}?format=j1"
    response = requests.get(base_url)
    data = response.json()
    return f"Temp in {city}: {data['current_condition'][0]['temp_C']}"


def what_is_bigger(n, m):
    if n > m:
        return f"{n} is bigger"
    elif m > n:
        return f"{m} is bigger"
    else:
        return f"{n} and {m} are equal"


def chat_with_ollama_no_functions(user_question):
    response = ollama.chat(
        model='llama3.1:8b-instruct-fp16',
        messages=[
            {'role': 'user', 'content': user_question}
        ]
    )
    return response


def chat_with_ollama(user_question):
    response = ollama.chat(
        model='llama3.1:8b-instruct-fp16',
        messages=[
            {'role': 'user', 'content': user_question}
        ],
        tools=[
            {
                'type': 'function',
                'function': {
                    'name': "get_current_weather",
                    'description': "Get the current weather for a city",
                    'parameters': {
                        'type': "object",
                        'properties': {
                            'city': {
                                'type': "string",
                                "description": "City",
                            },
                        },
                        'required': ['city'],
                    },
                },
            },
            {
                'type': "function",
                'function': {
                    "name": "which_is_bigger",
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'n': {
                                'type': "float",
                            },
                            "m": {
                                'type': "float"
                            },
                        },
                        'required': ['n', 'm'],
                    },
                },
            },
        ],
    )
    return response


def main():
    while True:
        user_input = input("Enter your question (or 'quit' to exit): ")
        if user_input.lower() == 'quit':
            break

        response = chat_with_ollama(user_input)

        if 'tool_calls' in response['message'] and response['message']['tool_calls']:
            tools_calls = response['message']['tool_calls']
            for tool_call in tools_calls:
                tool_name = tool_call['function']['name']
                arguments = tool_call['function']['arguments']

                if tool_name == 'get_current_weather' and 'city' in arguments:
                    result = get_current_weather(arguments['city'])
                    print("Weather function result:", result)
                elif tool_name == 'which_is_bigger' and 'n' in arguments and 'm' in arguments:
                    n, m = float(arguments['n']), float(arguments['m'])
                    result = what_is_bigger(n, m)
                    print("Comparison function result:", result)
                else:
                    print(f"No valid arguments found for function: {tool_name}")
        else:
            # If no tool calls or no valid arguments, use the LLM's response
            response = chat_with_ollama_no_functions(user_input)
            print("AI response:", response['message']['content'])


if __name__ == "__main__":
    main()
