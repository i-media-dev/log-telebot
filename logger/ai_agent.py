import logging
import os

from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_react_agent
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.language_models import LanguageModelLike
from langchain_gigachat.chat_models import GigaChat

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
        self._model = model
        self._tools = [find_and_read_log]

        prompt = PromptTemplate.from_template("""
            {system_prompt}

            У тебя есть следующие инструменты:
            {tools}

            Используй СТРОГО следующий формат:

            Вопрос: {input}

            Мысль: опиши, что нужно сделать
            Действие: одно из [{tool_names}]
            Аргументы: аргументы для действия
            Наблюдение: результат действия

            (ты можешь повторить Мысль/Действие/Наблюдение несколько раз)

            Финальный ответ: краткий и понятный ответ пользователю

            {agent_scratchpad}
        """)

        agent = create_react_agent(
            llm=model,
            tools=self._tools,
            prompt=prompt.partial(system_prompt=system_prompt),
            output_parser=ReActSingleInputOutputParser(),
        )

        self._executor = AgentExecutor(
            agent=agent,
            tools=self._tools,
            verbose=True,
            handle_parsing_errors=True
        )

    def ask(self, question: str) -> str:
        try:
            result = self._executor.invoke({
                "input": question
            })

            return result.get('output', '🤖 Ничего не могу сказать')

        except Exception:
            logging.exception('Ошибка в LlmAgent.ask')
            return '🤖 Ошибка при обработке запроса'
