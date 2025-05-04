from datetime import datetime
from typing import Union, Dict, List

import pytz
from llama_stack_client import AsyncLlamaStackClient
from llama_stack_client.types import UserMessage, ToolResponseMessage, ToolDefParam
from llama_stack_client.types.agents.turn import CompletionMessage
from llama_stack_client.types.shared_params.agent_config import AgentConfig

from oceanthundersbe import user_data
from oceanthundersbe.constants import LLAMA_STACK_URL, MODEL, ToolTypes
from oceanthundersbe.agents import SUPERVISOR_INSTRUCTIONS, AVAILABLE_AGENTS_FOR_SUPERVISOR
from oceanthundersbe.dto import InputMessage, UserData, AgentInstanceDetails, AgentDetails
from oceanthundersbe.service.utils import extract_agent_by_agent_name, execute_external_api, format_tools_for_llm


class LLMService:

    def __init__(self):
        print("LLM service has been initialized")
        self.client = AsyncLlamaStackClient(base_url=LLAMA_STACK_URL)

    async def handle_and_generate_response(self, data: InputMessage, connection_id: str) -> str:
        user_data_obj: UserData = user_data.get(connection_id)
        if user_data_obj.is_first_query or user_data_obj.current_task_agent is None:
            user_data_obj.is_first_query = False
            supervisor_response: CompletionMessage = await self.get_supervisor_response(user_data_obj, connection_id,
                                                                                        data)
            if supervisor_response.content:
                return supervisor_response.content
            elif supervisor_response.tool_calls:
                return await self.handle_task_agent(supervisor_response, connection_id, data, user_data_obj)
        else:
            return await self.handle_task_agent(None, connection_id, data, user_data_obj)

    async def get_supervisor_response(self, user_data_obj: UserData, connection_id: str, data: InputMessage):
        ist = pytz.timezone("Asia/Kolkata")
        now_ist = datetime.now(ist)
        formatted = now_ist.strftime("%Y-%m-%d %H:%M:%S %A")
        instructions = SUPERVISOR_INSTRUCTIONS.format(agents=AVAILABLE_AGENTS_FOR_SUPERVISOR, date=formatted)
        tools = []
        for agent in AVAILABLE_AGENTS_FOR_SUPERVISOR:
            tool = ToolDefParam(name=agent.get("name"), description=agent.get("description"),
                                parameters=agent.get("parameters"))
            tools.append(tool)
        agent_instance = user_data_obj.supervisor
        is_supervisor_call = True
        streaming = True
        agent_details: AgentDetails = AgentDetails(agent_name="", instructions=instructions, tools=tools)
        response: CompletionMessage = await self.get_llm_response(agent_details, agent_instance,
                                                                  is_supervisor_call, connection_id, streaming, data)
        return response

    async def get_llm_response(self, agent_details: AgentDetails, agent_instance: Union[AgentInstanceDetails, None],
                               is_supervisor_call: bool, connection_id: str, streaming: bool, data: InputMessage):
        try:
            ist = pytz.timezone("Asia/Kolkata")
            now_ist = datetime.now(ist)
            formatted = now_ist.strftime("%Y-%m-%d %H:%M:%S %A")
            instructions = agent_details.instructions.format(
                date=formatted) if '{date}' in agent_details.instructions else agent_details.instructions
            tools = agent_details.tools
            formatted_llm_tools = []
            if tools:
                formatted_llm_tools = await format_tools_for_llm(tools)
            print(f"formatted tools are: {formatted_llm_tools}")
            if agent_instance:
                agent_id = agent_instance.agent_id
                session_id = agent_instance.session_id
            else:
                agent = await self.client.agents.create(
                    agent_config=AgentConfig(
                        model=MODEL,
                        instructions=instructions,
                        client_tools=formatted_llm_tools,
                        enable_session_persistence=True,
                        max_infer_iters=100,
                        tool_choice="auto",
                    )
                )
                session = await self.client.agents.session.create(
                    agent_id=agent.agent_id,
                    session_name=f"session-{connection_id}",
                )
                agent_id = agent.agent_id
                session_id = session.session_id
                agent_instance = AgentInstanceDetails(agent_id=agent_id, session_id=session_id,
                                                      agent_name=agent_details.agent_name)
                if is_supervisor_call:
                    user_data[connection_id].supervisor = agent_instance
                else:
                    user_data[connection_id].current_task_agent = agent_instance

            input_message = UserMessage(role="user", content=data.content)
            while True:
                response = await self.client.agents.turn.create(
                    agent_id=agent_id,
                    session_id=session_id,
                    messages=[input_message] if not isinstance(input_message, list) else input_message,
                    stream=streaming,
                )
                turn = None
                async for chunk in response:
                    if chunk.event.payload.event_type == "turn_complete":
                        turn = chunk.event.payload.turn
                message: CompletionMessage = turn.output_message
                if not is_supervisor_call and message.tool_calls:
                    tool_responses = []
                    for tool_call in message.tool_calls:
                        tool_name = tool_call.tool_name
                        if tool_name == "Supervisor_Agent":
                            user_data[connection_id].current_task_agent = None
                            return await self.handle_and_generate_response(data, connection_id)
                        arguments = tool_call.arguments
                        call_id = tool_call.call_id
                        tool_response, is_agent_continued = await self.execute_tool_for_task_agent(tool_name, arguments,
                                                                                                   agent_details.tools,
                                                                                                   connection_id, data)
                        if is_agent_continued:
                            tool_responses.append(
                                ToolResponseMessage(role="tool", call_id=call_id, content=tool_response,
                                                    tool_name=tool_name))
                        else:
                            return tool_response
                    input_message = tool_responses
                else:
                    return message
        except Exception as e:
            print(f"Some exception while generating the llm response: {e}")

    async def handle_task_agent(self, supervisor_response: Union[None, CompletionMessage], connection_id: str,
                                data: InputMessage,
                                user_data_obj: UserData) -> str:
        agent_instance = user_data_obj.current_task_agent
        if not agent_instance:
            agent_name = supervisor_response.tool_calls[0].tool_name
            agent_details: AgentDetails = AgentDetails(**extract_agent_by_agent_name(agent_name))
        else:
            agent_details: AgentDetails = AgentDetails(**extract_agent_by_agent_name(agent_instance.agent_name))
        agent_response: Union[CompletionMessage, str] = await self.get_llm_response(agent_details,
                                                                        agent_instance, False, connection_id, True,
                                                                        data)
        return agent_response.content if isinstance(agent_response, CompletionMessage) else agent_response

    async def execute_tool_for_task_agent(self, tool_name: str, arguments: Dict, tools: List, connection_id: str,
                                          data: InputMessage):
        tool_info = next((tool for tool in tools if tool.get('name') == tool_name), None)
        if tool_info.get('tool_type') == ToolTypes.AGENT_TRANSFER.value:
            agent_details: AgentDetails = AgentDetails(**extract_agent_by_agent_name(tool_name))
            agent_response: CompletionMessage = await self.get_llm_response(agent_details,
                                                                            None, False, connection_id, True,
                                                                            data)
            return agent_response, False
        elif tool_info.get('tool_type') == ToolTypes.EXTERNAL_API_CALL.value:
            resp = await execute_external_api(tool_info, arguments)
            return resp, True
