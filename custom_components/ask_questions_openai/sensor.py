import openai
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_API_KEY, CONF_NAME
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.event import async_track_state_change
import logging

_LOGGER = logging.getLogger(__name__)
_LOGGER: logging.Logger = logging.getLogger(__package__)

DEFAULT_MODEL = "text-davinci-003"
CONF_MODEL = "model"

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

def ask_chat_gpt_sync(model, context, question, max_tokens, temperature):
    # Construct the prompt by combining the context and question
    if context is None:
        prompt = f"{question}"
    else:
        prompt = f"Context: {context}\nQuestion: {question}"

    _LOGGER.debug("Prompt is: " + prompt)
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

    except openai.OpenAIError as error:
        if error.status == 401:
            _LOGGER.error("Invalid API key.")
            return None
        else:
            _LOGGER.error("An error occurred while making the API request.")
            return None

    except Exception as e:
        _LOGGER.error("An unexpected error occurred: %s", {str(e)})
        return None

    # Extract and return the answer from the response
    answer = response.choices[0].text.strip()
    return answer


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

    async def async_ask_chat_gpt(self, entity_id, old_state, new_state):
        if (old_state and new_state and old_state.attributes['input_question'] != new_state.attributes['input_question']) or (not old_state and new_state):
            if not new_state.attributes['input_question']:
                self._state = "missing input"
                self.async_write_ha_state()
                pass
            _LOGGER.debug("Detected change in the input question")
            response = await self._hass.async_add_executor_job(
                ask_chat_gpt_sync,
                self._model,
                self.new_state.attributes['input_question'],
                self.new_state.attributes['input_context'],
                964,
                0.9
            )
            _LOGGER.debug("Response is: " + response)
            self._output_response = response
            if response is None:
                self._state = "error"
            else:
                self._state = "received"
            self.async_write_ha_state()

    async def async_added_to_hass(self):
        _LOGGER.debug("Added AskQuestionsOpenAI sensor to hass")
        async_track_state_change(
            self._hass, self.entity_id, self.async_ask_chat_gpt
        )

    async def async_update(self):
        pass
