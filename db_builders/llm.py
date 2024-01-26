from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI

load_dotenv()

GPT3_LOW_T = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.3)
GPT3_HIGH_T = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.9)
