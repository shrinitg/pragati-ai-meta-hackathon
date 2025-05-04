import json

import emoji
import requests
from llama_stack_client.types.tool_def_param import Parameter, ToolDefParam

from oceanthundersbe.agents import AVAILABLE_AGENTS


def extract_agent_by_agent_name(agent_name) -> dict:
    return next((agent for agent in AVAILABLE_AGENTS if agent.get("agent_name") == agent_name), None)


async def execute_external_api(tool_info, arguments):
    method = tool_info.get("api_details").get("method", "get").lower()
    url = tool_info.get("api_details")["url"]
    body = arguments
    try:
        if method == "post":
            response = requests.post(url, json=body)
        elif method == "put":
            response = requests.put(url, json=body)
        elif method == "patch":
            response = requests.patch(url, json=body)
        elif method == "delete":
            if "appointment_id" in body:
                url += f'/{body.get("appointment_id")}'
            if "order_id" in body:
                url += f'/{body.get("order_id")}'
            response = requests.delete(url)
        else:
            response = requests.get(url)

        print(f"Status Code: {response.status_code}")
        print("Response JSON:", response.json())
        return json.dumps(response.json())

    except requests.RequestException as e:
        print(f"API request failed: {e}")


async def format_tools_for_llm(tools):
    final_tools = []
    for tool in tools:
        tools_params = []
        for parameter in tool.get("parameters"):
            param = Parameter(
                name=parameter.get("name"),
                parameter_type=parameter.get("parameter_type"),
                default=None,
                required=parameter.get("required"),
                description=parameter.get("description"),
            )
            tools_params.append(param)
        tool_def_param = ToolDefParam(
            description=tool.get("description"),
            name=tool.get("name"),
            parameters=tools_params,
        )
        final_tools.append(tool_def_param)
    return final_tools


def remove_emojis(text):
    try:
        return emoji.replace_emoji(text, replace='')
    except Exception as e:
        return text
