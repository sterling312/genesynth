import os
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass, field

import numpy as np
import openai
from genesynth.types import BaseMask
from genesynth.extensions import extensions

@extensions.register(['openai'])
@dataclass(unsafe_hash=True)
class BaseGenaiFixture(BaseMask):
    base_url = None
    env_var = 'OPENAI_API_KEY'

    prompt: str
    model: str = 'gpt-4o-mini'

    @property
    def api_key(self):
        return os.environ.get(self.env_var)

    async def generate(self):
        arr = []
        for _ in range(self.size):
            cli = openai.AsyncOpenAI(base_url=self.base_url, api_key=self.api_key)
            data = dict(role='user', content=self.prompt)
            stream = await cli.chat.completions.create(model=self.model, messages=[data], stream=True)
            text = ''.join([chunk.choices[0].delta.content or '' async for chunk in stream])
            arr.append(text.replace('\n', ' '))
        arr = np.array(arr)
        return self.apply_index(arr)


@extensions.register(['ollama'])
@dataclass(unsafe_hash=True)
class OllamaFixture(BaseGenaiFixture):
    base_url = 'http://localhost:11434/v1'

    prompt: str
    model: str = 'llama3.1:8b'

    @property
    def api_key(self):
        return 'fake_key'


@extensions.register(['google'])
@dataclass(unsafe_hash=True)
class GoogleFixture(BaseGenaiFixture):
    _base_url = 'https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT}/locations/{LOCATION}/endpoints/openapi'

    prompt: str
    model: str = 'gemini-1.5-flash-001'

    @property
    def base_url(self):
        import google.auth as google_auth
        creds, project = google_auth.default()
        location = os.environ.get('LOCATION', 'us-central1')
        return self._base_url.format(PROJECT=project, LOCATION=location)

    @property
    def api_key(self):
        import google.auth
        import google.auth.transport.requests
        creds, project = google.auth.default()
        auth_req = google.auth.transport.requests.Request()
        creds.refresh(auth_req)
        return creds.token

