# import logging
import os

from dotenv import load_dotenv
# from langchain.agents import AgentExecutor, create_react_agent
# from langchain.agents.output_parsers import ReActSingleInputOutputParser
# from langchain.prompts import PromptTemplate
from langchain_core.language_models import LanguageModelLike
from langchain_gigachat.chat_models import GigaChat
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
            system_prompt=system_prompt,
        )

    def ask(self, question: str) -> str:
        result = self._agent.invoke({
            "messages": [
                {"role": "user", "content": question}
            ]
        })
        return result["messages"][-1]["content"]
