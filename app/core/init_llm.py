# init_llm.py
import os
from typing import Optional


try:
   # Loads .env if present (safe to keep optional)
   from dotenv import load_dotenv
   load_dotenv()
except Exception:
   pass


from langchain_openai import ChatOpenAI


def make_llm(
   model: Optional[str] = None,
   max_retries=1,
   temperature: Optional[float] = None,
) -> ChatOpenAI:
   api_key = os.getenv("OPENAI_API_KEY")
   if not api_key:
       raise RuntimeError(
           "OPENAI_API_KEY is not set. Create a `.env` with your key or set it in the environment."
       )
   model = model or os.getenv("OPENAI_MODEL", "gpt-4")
   temperature = float(temperature if temperature is not None
                       else os.getenv("OPENAI_TEMPERATURE", "0.5"))
   max_retries=max_retries;
   return ChatOpenAI(model=model, temperature=temperature,max_retries=max_retries)