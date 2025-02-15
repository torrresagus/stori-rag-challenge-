import os

from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langfuse.callback import CallbackHandler

from app.constants.openai_models import OpenAIModels
from app.utils.logger import logger

load_dotenv(override=True)


class BaseAgent:
    """Base agent class for handling LLM interactions.

    Attributes:
        correlation_id (str): Unique identifier for tracking requests
        model_openai (OpenAIModels): OpenAI model to use
        temperature_openai (float): Temperature parameter for model responses
        run_name (str): Name identifier for the run
        langfuse_handler (CallbackHandler): Handler for Langfuse logging
        llm (ChatOpenAI): OpenAI chat model instance
    """

    def __init__(
        self,
        run_name: str = "",
        correlation_id: str = "",
        model_openai: OpenAIModels = OpenAIModels.GPT_4O_MINI,
        temperature_openai: float = 0,
    ):

        self.correlation_id = correlation_id
        self.model_openai = model_openai
        self.temperature_openai = temperature_openai

        self.run_name = run_name

        self.langfuse_handler = CallbackHandler(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST"),
            session_id=self.correlation_id,
        )

        self.llm = ChatOpenAI(
            model=self.model_openai,
            temperature=self.temperature_openai,
        )

    def run(
        self,
        prompt: ChatPromptTemplate,
        input_data: dict,
        tags: list[str] = None,
        metadata: dict = None,
    ) -> str:
        """Execute the LLM chain with the given prompt and input data.

        Args:
            prompt (ChatPromptTemplate): Template for the chat prompt
            input_data (dict): Input data for the prompt
            tags (list[str], optional): Tags for tracking. Defaults to None.
            metadata (dict, optional): Additional metadata. Defaults to None.

        Returns:
            str: The model's response

        Raises:
            Exception: If an error occurs during execution
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
