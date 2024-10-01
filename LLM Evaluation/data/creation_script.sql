CREATE DATABASE IF NOT EXISTS SAMPLEDATABASE;
CREATE OR REPLACE SCHEMA LLM_EVAL;
USE SCHEMA LLM_EVAL;

CREATE OR REPLACE TABLE AI_FEEDBACK (
    USER VARCHAR,
    TOPIC VARCHAR,
    MODEL VARCHAR,
    CATEGORY VARCHAR,
    SCORE NUMBER,
    CONVERSATION VARCHAR,
    COMMENTS VARCHAR,
    FLAGGED BOOLEAN,
    REASON VARCHAR
);

CREATE OR REPLACE TABLE USERS (
    USERNAME VARCHAR
);

INSERT INTO USERS(
    USERNAME
)
VALUES ('Snow');

-- Creation of the OpenAI API Integration
CREATE OR REPLACE SECRET open_ai_api_secret
    TYPE = GENERIC_STRING
    SECRET_STRING = 'YOUR_OPENAI_API_KEY';

CREATE OR REPLACE NETWORK RULE openai_network_rule
    MODE = EGRESS
    TYPE = HOST_PORT
    VALUE_LIST = ('api.openai.com');

CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION openai_access_integration
    ALLOWED_NETWORK_RULES = (openai_network_rule)
    ALLOWED_AUTHENTICATION_SECRETS = (open_ai_api_secret)
    ENABLED = true;

CREATE OR REPLACE FUNCTION GPT_COMPLETION(model VARCHAR, prompt VARCHAR)
RETURNS STRING
LANGUAGE PYTHON
RUNTIME_VERSION = 3.9
HANDLER = 'get_completion'
EXTERNAL_ACCESS_INTEGRATIONS = (openai_access_integration)
SECRETS = ('openai_key' = open_ai_api_secret)
PACKAGES = ('openai')
AS
$$
import _snowflake
from openai import OpenAI
def get_completion(MODEL: str, PROMPT: str) -> str:
    client = OpenAI(api_key=_snowflake.get_generic_secret_string("openai_key"))
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": PROMPT,
            },
        ],
    )
    return completion.choices[0].message.content
$$;

-- Table to feed the Cortex Search Service
CREATE TABLE SUSTAINABLE_ENERGY (
    DESCRIPTION VARCHAR,
    TYPE VARCHAR,
    ID NUMBER
);

INSERT INTO
    SUSTAINABLE_ENERGY (DESCRIPTION, TYPE, ID)
VALUES
    (
        'Solar Power
        Solar power is one of the most promising sources of renewable energy, harnessing the abundant energy of the sun to generate electricity.
        Photovoltaic (PV) cells, commonly found in solar panels, convert sunlight directly into electricity, offering a clean and sustainable alternative to fossil fuels.
        Advancements in solar technology have significantly reduced the cost of solar panels, making them more accessible for residential, commercial, and industrial use.
        In addition to rooftop installations, solar farms are being developed worldwide, capable of generating large amounts of electricity to power entire communities.
        Innovations such as solar tracking systems and solar storage solutions continue to improve efficiency, ensuring that solar power remains a key component of the global shift toward renewable energy.',
        'Solar Power',
        1
    ),
    (
        'Wind Energy
        Wind energy is another leading renewable energy source, utilizing the power of wind to generate electricity.
        Wind turbines, often grouped together in wind farms, capture the kinetic energy of wind and convert it into electrical energy.
        Offshore wind farms, located in bodies of water, are particularly effective due to the stronger and more consistent wind patterns found over the ocean.
        As technology advances, wind turbines are becoming larger and more efficient, capable of generating more power with less impact on the environment.
        Wind energy is seen as a crucial element in reducing greenhouse gas emissions, with many countries setting ambitious targets to increase their wind energy capacity in the coming decades.',
        'Wind Energy',
        2
    ),
    (
        'Hydroelectric Power
        Hydroelectric power, or hydropower, is one of the oldest and most established forms of renewable energy.
        It generates electricity by using the gravitational force of falling or flowing water, typically through dams built on large rivers.
        The water flows through turbines, spinning them to generate electricity.
        Hydropower is highly reliable and can be adjusted to meet peak electricity demands, making it a valuable resource for grid stability.
        However, the construction of large dams can have significant environmental and social impacts, such as the displacement of communities and disruption of local ecosystems.
        Despite these challenges, hydroelectric power remains a critical source of clean energy, especially in regions with abundant water resources.',
        'Hydroelectric Power',
        3
    ),
    (
        'Advancements in Battery Technology
        As renewable energy sources like solar and wind become more prevalent, the need for efficient energy storage solutions has become increasingly important.
        Battery technology plays a crucial role in storing energy generated from renewable sources, allowing it to be used when the sun isn’t shining or the wind isn’t blowing.
        Recent advancements in battery technology, particularly in lithium-ion batteries, have led to significant improvements in energy density, cost, and lifespan.
        Innovations such as solid-state batteries and flow batteries promise even greater efficiency and safety, with the potential to revolutionize energy storage.
        These advancements are not only vital for grid storage but also for the growing electric vehicle market, where long-lasting, fast-charging batteries are key to widespread adoption.',
        'Advancements in Battery Technology',
        4
    ),
    (
        'Policy and Implementation of Green Energy Initiatives
        The global transition to renewable energy is not just about technology;
        it also requires robust policies and effective implementation strategies.
        Governments around the world are developing policies to encourage the adoption of green energy,
        such as subsidies for renewable energy projects, tax incentives for clean energy investments,
        and regulations to reduce carbon emissions. International agreements, like the Paris Agreement,
        play a crucial role in setting targets for reducing greenhouse gas emissions and promoting sustainable energy practices.
        Successful implementation of green energy initiatives requires collaboration between governments,
        private companies, and communities. Challenges such as financing, infrastructure development,
        and public acceptance must be addressed to ensure a smooth transition to a sustainable energy future.',
        'Policy and Implementation of Green Energy Initiatives',
        5
    ),
    (
        'Future Trends in Renewable Energy
        The future of renewable energy is bright, with continued innovation and investment driving the sector forward.
        Trends such as the integration of artificial intelligence and machine learning into energy management systems are helping to optimize the production and distribution of renewable energy.
        The rise of decentralized energy systems, where energy is produced and consumed locally, is also gaining traction, particularly in rural and remote areas.
        Additionally, the development of hybrid renewable energy systems, combining multiple sources such as solar and wind, is increasing the reliability and efficiency of renewable energy generation.
        As the world moves toward a carbon-neutral future, the renewable energy industry is expected to grow exponentially, creating new opportunities for innovation, job creation, and economic development.',
        'Future Trends in Renewable Energy',
        6
    );

-- Creation of the Cortex Search Service
CREATE OR REPLACE CORTEX SEARCH SERVICE SUSTAINABLE_ENERGY_SERVICE
ON DESCRIPTION
ATTRIBUTES TYPE
WAREHOUSE = SAMPLE_WH
TARGET_LAG = '1 day'
AS (
    SELECT
        DESCRIPTION,
        TYPE,
        ID
    FROM SUSTAINABLE_ENERGY
);