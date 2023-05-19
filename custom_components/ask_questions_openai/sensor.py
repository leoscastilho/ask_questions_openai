import logging

import openai
import multiprocessing
import signal
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_API_KEY, CONF_NAME
import homeassistant.helpers.config_validation as cv
from homeassistant.core import callback

DEFAULT_MODEL = "text-davinci-003"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_KEY): cv.string,
        vol.Required(CONF_NAME): cv.string,
        vol.Optional(CONF_MODEL, default=DEFAULT_MODEL): cv.string,
    }
)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    api_key = config[CONF_API_KEY]
    name = config[CONF_NAME]
    model = config[CONF_MODEL]

    openai.api_key = api_key

    async_add_entities([AskQuestionsOpenAISensor(hass, name, model)], True)

def ask_chat_gpt_sync(model,context, question, max_tokens,temperature):
    # Construct the prompt by combining the context and question
    prompt = f"Context: {context}\nQuestion: {question}\nAnswer:"

    # Create a function to handle timeouts
    def timeout_handler(signum, frame):
        raise TimeoutError("API call timed out.")

    # Set the timeout duration (in seconds)
    timeout_duration = 10

    # Set up the timeout handler
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_duration)

    try:
        # Generate a response from the ChatGPT model
        response = openai.Completion.create(
            engine=model,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            n=1,
            stop=None
        )

        # Cancel the timeout if the API call returns within the timeout duration
        signal.alarm(0)

        # Extract and return the answer from the response
        answer = response.choices[0].text.strip()
        return answer

    except TimeoutError as e:
        return str(e)

class AskQuestionsOpenAISensor(SensorEntity):
    def __init__(self, hass, name, model):
        self._hass = hass
        self._name = name
        self._model = model
        self._state = None
        self._input_context = ""
        self._input_question = ""
        self._output_response = ""

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def model(self):
        return self._model

    @property
    def input_context(self):
        return self._input_context

    @property
    def input_question(self):
        return self._input_question

    @property
    def output_response(self):
        return self._output_response


    @property
    def extra_state_attributes(self):
        return {"input_context": self._input_context,
                "input_question": self._input_question,
                "output_response": self._output_response}

    def on_question_change(self):
        if self._input_question:
            self._state = "querying"
            self._output_response = "Asking GPT..."
            gpt_response = ask_chat_gpt_sync(
                self._model,
                self._input_context,
                self._input_question,
                964,
                0.9
            )
            self._output_response = gpt_response["choices"][0]["text"]
            self._state = "received"
            self.async_write_ha_state()
        else:
            logging.WARN("Input is required to query GPT")
            self._state = "error"


    async def async_added_to_hass(self):
        self.async_on_remove(
            self._hass.helpers.event.async_track_state_change(
                "input_text.gpt_input", self.async_generate_openai_response
            )
        )

    async def async_update(self):
        pass