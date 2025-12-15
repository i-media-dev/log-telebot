from dotenv import load_dotenv
from langchain.agents import create_react_agent
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.language_models import LanguageModelLike
from langchain_gigachat.chat_models import GigaChat

from logger.constants_ii import PROMPT
from logger.ii_tools import find_and_read_log

load_dotenv()

model = GigaChat(
    model="GigaChat-2-Max",
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
        response = self._agent.invoke({"input": question})
        return str(response)
