# app/core/agents/base_agent.py
import os
from typing import List, Optional, Union

from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_postgres import PostgresChatMessageHistory
from langfuse.callback import CallbackHandler

from app.constants.openai_models import OpenAIModels
from app.utils.logger import logger

load_dotenv(override=True)


class BaseAgent:
    """
    Base agent that supports two modes of execution:
      - run(): Executes the LLM chain without modifying the memory.
      - chat(): Injects the history (if exists) into the input data and
                updates the chat history with the exchange.
    """

    def __init__(
        self,
        run_name: str = "",
        correlation_id: str = "",
        session_id: str = "",
        model_openai: OpenAIModels = OpenAIModels.GPT_4O_MINI,
        temperature_openai: float = 0,
        chat_history: Optional[PostgresChatMessageHistory] = None,
    ):
        self.correlation_id = correlation_id
        self.session_id = session_id
        self.model_openai = model_openai
        self.temperature_openai = temperature_openai
        self.chat_history = chat_history
        self.run_name = run_name

        self.langfuse_handler = CallbackHandler(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST"),
            session_id=(
                self.session_id if self.session_id else self.correlation_id
            ),
        )

        self.llm = ChatOpenAI(
            model=self.model_openai,
            temperature=self.temperature_openai,
        )

    def _add_to_chat_history(
        self, messages: List[Union[SystemMessage, HumanMessage, AIMessage]]
    ) -> None:
        """
        Adds messages to the chat history (if memory is enabled).
        """
        if self.chat_history:
            try:
                self.chat_history.add_messages(messages)
            except Exception as e:
                logger.error("Error at saving chat history: %s", e)

    def run(
        self,
        prompt: ChatPromptTemplate,
        input_data: dict,
        tags: List[str] = None,
        metadata: dict = None,
    ) -> str:
        """
        Executes the LLM chain without modifying the memory.

        Args:
            prompt (ChatPromptTemplate): The prompt template.
            input_data (dict): Data to fill the template.
            tags (List[str], optional): Tags for logging.
            metadata (dict, optional): Additional metadata for logging.

        Returns:
            str: The model's response.
        """
        tags = tags or []
        metadata = metadata or {}

        config = {
            "run_name": self.run_name,
            "callbacks": [self.langfuse_handler],
            "tags": tags,
            "metadata": metadata,
        }

        try:
            llm_chain = prompt | self.llm
            response = llm_chain.invoke(input_data, config=config)
            return response
        except Exception as e:
            logger.error(f"An error occurred with {self.model_openai}: {e}")
            raise Exception(
                f"An error occurred with {self.model_openai}: {e}"
            ) from e

    def chat(
        self,
        prompt: ChatPromptTemplate,
        input_data: dict,
        user_message: str,
        tags: List[str] = None,
        metadata: dict = None,
    ) -> str:
        """
        Executes the LLM chain and, if memory is enabled:
          - Injects the previous history (if not explicitly passed) into the input data.
          - Then, registers in the memory the user's message and the model's response.

        Args:
            prompt (ChatPromptTemplate): The prompt template.
            input_data (dict): Data to fill the template.
            user_message (str): The user's message to be used to update the memory.
            tags (List[str], optional): Tags for logging.
            metadata (dict, optional): Additional metadata for logging.

        Returns:
            str: The model's response.
        """
        if self.chat_history and "chat_history" not in input_data:
            input_data["chat_history"] = self.chat_history.messages

        response = self.run(prompt, input_data, tags, metadata)

        if self.chat_history:
            message_content = (
                response.content if hasattr(response, "content") else response
            )
            self._add_to_chat_history(
                [
                    HumanMessage(content=user_message),
                    AIMessage(content=message_content),
                ]
            )
        return response
