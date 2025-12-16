# import logging
import os
import uuid

from dotenv import load_dotenv
# from langchain.agents import AgentExecutor, create_react_agent
# from langchain.agents.output_parsers import ReActSingleInputOutputParser
# from langchain.prompts import PromptTemplate
from langchain_core.language_models import LanguageModelLike
from langchain_core.runnables import RunnableConfig
from langchain_gigachat.chat_models import GigaChat
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent

from logger.ai_tools import find_and_read_log
from logger.constants_ai import PROMPT
from logger.logging_config import setup_logging

load_dotenv()
setup_logging()

gigachat_key = os.getenv('GIGACHAT_API_KEY')

model = GigaChat(
    model="GigaChat-2-Max",
    credentials=gigachat_key,
    verify_ssl_certs=False,
)

system_prompt = PROMPT


class LlmAgent:
    def __init__(self, model: LanguageModelLike):
        self._tools = [find_and_read_log]

        self._agent = create_react_agent(
            model=model,
            tools=self._tools,
            prompt=system_prompt,
            checkpointer=InMemorySaver()
        )
        self._config: RunnableConfig = {
            "configurable": {"thread_id": uuid.uuid4().hex}}

    def ask(self, question: str) -> str:
        result = self._agent.invoke(
            {"messages": [{"role": "user", "content": question}]},
            config=self._config
        )
        return result["messages"][-1].content
