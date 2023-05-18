DOMAIN = "ask_questions_openai"

ATTR_NAME = "name"
DEFAULT_NAME = "World"


def setup(hass, config):
    """Set up is called when Home Assistant is loading our component."""

    def handle_ask_questions_openai(call):
        """Handle the service call."""
        name = call.data.get(ATTR_NAME, DEFAULT_NAME)

        hass.states.set("hello_service.hello", name)

    hass.services.register(DOMAIN, "hello", handle_hello)

    # Return boolean to indicate that initialization was successful.
    return True