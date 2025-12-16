import os
import logging

from dotenv import load_dotenv
from langchain.agents import create_react_agent
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.language_models import LanguageModelLike
from langchain_gigachat.chat_models import GigaChat
from logger.logging_config import setup_logging

from logger.ai_tools import find_and_read_log
from logger.constants_ai import PROMPT

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
        self._model = model
        self._tools = [find_and_read_log]

        prompt = PromptTemplate.from_template("""
            {system_prompt}
            Запрос: {input}
            Действуй.
        """)

        self._agent = create_react_agent(
            llm=model,
            tools=self._tools,
            prompt=prompt.partial(system_prompt=system_prompt),
            output_parser=ReActSingleInputOutputParser(),
            stop_sequence=True
        )

    def ask(self, question: str) -> str:
        try:
            response = self._agent.invoke({
                "input": question
            })
            if hasattr(response, 'output'):
                logging.info(
                    'В ask получен ответ output: %s',
                    str(response.output)
                )
                return str(response.output)
            else:
                logging.info(
                    'В ask получен ответ: %s',
                    str(response)
                )
                return str(response)
        except Exception as error:
            return f'Ошибка: {error}'
