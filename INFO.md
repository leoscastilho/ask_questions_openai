# ask_questions_openai
HASS Custom Component to Call Open AI's API for Completion

Add to the configuration.yaml file:

    - platform: ask_questions_openai
      api_key: OPENAI_API_KEY
      model: "text-davinci-003" # Optional, defaults to "text-davinci-003"
      name: "open_ai_response_test"
