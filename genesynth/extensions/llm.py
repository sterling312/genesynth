import os
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass, field

import numpy as np
import ollama
import openai
from genesynth.types import BaseMask
from genesynth.extensions import extensions

@extensions.register(['llama'])
@dataclass(unsafe_hash=True)
class BaseLlamaFixture(BaseMask):
    prompt: str
    model: str = 'llama2:7b'

    async def generate(self):
        arr = []
        cli = ollama.AsyncClient()
        for _ in range(self.size):
            data = dict(role='user', content=self.prompt)
            stream = await cli.chat(model=self.model, messages=[data], stream=True)
            text = ''.join([chunk['message']['content'] or '' async for chunk in stream])
            arr.append(text.replace('\n', ' '))
        arr = np.array(arr)
        return self.apply_index(arr)


@extensions.register(['gemma'])
@dataclass(unsafe_hash=True)
class GemmaFixture(BaseLlamaFixture):
    prompt: str
    model: str = 'gemma:2b'


@extensions.register(['chatgpt'])
@dataclass(unsafe_hash=True)
class ChatGptFixture(BaseMask):
    prompt: str
    model: str = 'gpt-3.5-turbo'
    env_var: str = 'OPENAI_API_KEY'
    temperature: float = 0.8

    async def generate(self):
        arr = []
        for _ in range(self.size):
            cli = openai.AsyncOpenAI(api_key=os.environ.get(self.env_var))
            data = dict(role='user', content=self.prompt)
            stream = await cli.chat.completions.create(model=self.model, messages=[data], temperature=self.temperature, stream=True)
            text = ''.join([chunk.choices[0].delta.content or '' async for chunk in stream])
            arr.append(text.replace('\n', ' '))
        arr = np.array(arr)
        return self.apply_index(arr)

