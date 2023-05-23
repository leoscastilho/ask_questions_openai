# ask_questions_openai
HASS Custom Component to Call Open AI's API for Completion

## Requirement
This sensor requires the Python Script set_state. Copy this file to the path: `HASSCONFIG/python_scripts`


## How to use
### Below an Example of how to use this sensor to generate a random Poem when clicking a button.

### 1 - Import the sensor
First include the sensor in your configuration file. After this you need to reboot HASS.
```yaml
# configuration.yaml

sensor:
  - platform: ask_questions_openai  # Required: Name of the integration [Don't change this]
    api_key: YOR_API_KEY            # Required: Plain text or Secret [Update with your API key]
    name: "open_ai_response_poem"   # Required: Name of the sensor to be used within HASS [Update with a meaningful name]
    model: "text-davinci-003"       # Optional: Defaults to "text-davinci-003" [Update with other models if desired]
    
    ... # You can add more sensors for different purposes referencing the same platform, giving it a different "name"
```

### 2 - Create a Button
Go to Settings -> Devices & Services -> Helpers -> Create Helper -> Button

Give it a meaningful name: Generate Random Poem (this will give the button the alias: input_button.generate_random_poem)


### 3 - Crete an automation
You can then create an Automation.

Go to Settings -> Automations and Scenes -> Create Automation -> Create New Automation

Click on the tree dots on the top right side and switch to `Edit in YAML`

```yaml
# New Automation
alias: Generate a Random Poem
description: "Generate a Random Poem when clicking a button"
trigger:
  - platform: state
    entity_id: input_button.generate_random_poem  # The alias of the button you created
condition: []
action:
- service: python_script.set_state           # The set_state python script is required for this sensor to work
data_template:
  entity_id: sensor.open_ai_response_poem    # Name of the sensor you imported in the configuration.yaml file
  output_response: Generating a poem ...     # Text to show in the dashboard while it is waiting for a response
  # Input Context: Add context to the API before your question
  # Input Question: Actual question
  input_context: >-
    I want you to act as a poet. You will create poems that evoke emotions
    and have the power to stir people’s soul. Your poem will be 4
    paragraphers long but make sure your words convey the feeling you are
    trying to express in beautiful yet meaningful ways. You can also come up
    with short verses that are still powerful enough to leave an imprint in
    readers' minds.
  input_question: >-
    Write a poem about today. Today is
    {{['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'][now().weekday()]}},
    {{['January','February','March','April','May','June','July','August','September','October','November','December'][now().month-1]}}
    {{['1st','2nd','3rd','4th','5th','6th','7th','8th','9th','10th','11th','12th','13th','14th','15th','16th','17th','18th','19th','20th','21st','22nd','23rd','24th','25th','26th','27th','28th','29th','30th','31st'][now().day-1]
    }}, {{ now().year }}. The day is {{ states('weather.home') }} and I'm
    feeling
    {{["Joyful","Courageous","Grateful","Content","Excited","Enthusiastic","Serene","Inspired","Motivated","Curious","Fulfilled","Loved"]|
    random }}
```

Example of how the prompt to the API would look like:

    Context: Poetry is the ethereal dance of words, weaving emotions into a tapestry of vivid imagery and profound meaning. In this poetic endeavor, I shall endeavor to create a masterpiece that stirs the depths of the human soul. Through four exquisite paragraphs or even brief verses, I shall strive to evoke powerful emotions, leaving an indelible imprint upon the readers' minds. With each word carefully chosen, let the beauty and depth of my poetry resonate with your very being. The poem should be 4 paragraphs long.
    Question: Write a poem about today. Today is Tuesday, May 23rd, 2023. The day is sunny and I'm feeling Courageous

### 4 - Create a new card in the dashboard
Go to your dashboard -> Edit dashboard -> + ADD CARD -> Manual

Paste the Code below to create a Card with a button and a text markdown for your response

```yaml
type: grid
square: false
columns: 1
cards:
  - show_name: true
    show_icon: true
    type: button
    entity: input_button.generate_random_poem
    icon_height: 30px
    tap_action:
      action: toggle
    hold_action:
      action: none
  - type: markdown
    content: '{{ state_attr(''sensor.open_ai_response_poem'',''output_response'') }}'

```