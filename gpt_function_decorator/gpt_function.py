from functools import wraps
import typing

import pydantic
from openai import OpenAI

from . import arg_utils

# This is a global variable that will store the OpenAI client. This
# enables any user to set the client  under their own terms (key, project...)
# via `gpt_function.SETTINGS["openai_client"] = OpenAI()`.
# If the user doesn't set up the client, it gets set up automatically with
# OpenAI() the first time a client is needed
SETTINGS = {"docgptor_openai_client": None}

ADDITIONAL_DOCS = """

Function auto-generated by @docgpt.
- The execution happens on a chatbot, and may require an API key.
- Answers can be changing, their quality and validity are not guaranteed.
- The following auto-added parameters can control the GPT execution:

Parameters
-----------

gpt_model: str
    The OpenAI model, current choices are gpt-4o-mini, gpt-4o-2024-08-06, and later.
    `gpt-4o-mini` is faster, and 10 times less expensive, but the answers can be
    less good.

gpt_system_prompt: Optional[str]
    Additional prompt to be added before the user's prompt. This can be used
"""


def docgpt(func):
    """Decorator that runs a function on a GPT model."""

    requested_format = typing.get_type_hints(func).get("return", str)
    if not isinstance(requested_format, pydantic.BaseModel):

        class __Response(pydantic.BaseModel):
            response: requested_format

        requested_format = __Response

    @arg_utils.add_kwargs(gpt_model="gpt-4o-mini", gpt_system_prompt=None)
    @wraps(func)  # This preserves the docstring and other attributes
    def wrapper(*args, **kwargs):
        # Get and remove parameters used by the wrapper only
        gpt_model = kwargs.pop("gpt_model")
        gpt_system_prompt = kwargs.pop("gpt_system_prompt")

        all_named_args = arg_utils.name_all_args_and_defaults(func, args, kwargs)

        prompt = arg_utils.generate_prompt_from_docstring(func.__doc__, all_named_args)

        system_prompt = "Answer using the provided output schema."
        if gpt_system_prompt:
            # Add user provided prompt
            system_prompt = gpt_system_prompt + "\n" + system_prompt
        gpt_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        # Initiate the global GPT client if it's not already set
        client = SETTINGS["openai_client"]
        if client is None:
            client = SETTINGS["openai_client"] = OpenAI()

        # Query the GPT model, extract the response
        response = client.beta.chat.completions.parse(
            messages=gpt_messages, model=gpt_model, response_format=requested_format
        )
        formatted_response = response.choices[0].message.parsed
        if formatted_response.__class__.__name__ == "__Response":
            formatted_response = formatted_response.response

        return formatted_response

    # Add a text to the docstring so it will be clear to users that the
    # function is actually running on a chatbot.
    wrapper.__doc__ += ADDITIONAL_DOCS
    return wrapper


def ReasonedAnswer(T) -> pydantic.BaseModel:
    """Return a new type that includes a reasoning string with the result.

    The reasoning will be in `myvariable.reasoning`, and the result with the
    originally requested type T will be in `myvariable.result`.
    """

    class _ReasonedAnswer(pydantic.BaseModel):
        reasoning: str
        result: T

        def __str__(self):
            return f"{self.result}\n\nGPT reasoning: {self.reasoning}"

    return _ReasonedAnswer
