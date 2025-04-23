# from google.genai import types
# from google import genai
import google.generativeai as genai, types

functions = [
    {
        "name": "get_lists_of_strings",
        "description": "Trả về danh sách các danh sách con, mỗi danh sách gồm 3 chuỗi",
        "parameters": {
            "type": "object",
            "properties": {}
        },
        "returns": {
            "type": "array",
            "items": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "minItems": 3,
                "maxItems": 3
            }
        }
    }
]

tools = types.Tool(function_declarations=[function])
config = types.GenerateContentConfig(tools=[tools])

client = genai.Client(api_key="pass")

contents = [
    types.Content(
        role="user", parts=[types.Part(text="Turn the lights down to a romantic level")]
    )
]

# Send request with function declarations
response = client.models.generate_content(
    model="gemini-2.0-flash", config=config, contents=contents
)

tool_call = response.candidates[0].content.parts[0].function_call

if tool_call.name == "set_light_values":
    # result = set_light_values(**tool_call.args)
    # print(f"Function execution result: {result}")
    pass

def component_in_node4j(list: list[tuple[str,str,str]]):
    pass


def Ans(Text):
    pass