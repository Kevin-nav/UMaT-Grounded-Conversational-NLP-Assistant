DIRECT_LOOKUP_USER_TEMPLATES = (
    "Tell me about {name}.",
    "Who is {name}?",
    "Can you tell me about {name}?",
)

DIRECT_LOOKUP_RESPONSE_TEMPLATES = (
    "{name} is {role} in the {department_name}.",
    "{name} works as {role} in the {department_name}.",
    "{name} is part of the {department_name} as {role}.",
)

FOLLOW_UP_LOCATION_USER_TEMPLATES = (
    "Where is {pronoun} office?",
    "How do I find {pronoun} office?",
    "Can you tell me where {pronoun} is located?",
)

FOLLOW_UP_LOCATION_RESPONSE_TEMPLATES = (
    "{name} is based at {campus}. {directions}",
    "{name}'s office is at {campus}. {directions}",
    "You can find {name} at {campus}. {directions}",
)

GREETING_USER_TEMPLATES = (
    "Hello, I need help finding {name}.",
    "Hi, can you help me with {name}?",
    "Good day, tell me about {name}.",
)

GREETING_RESPONSE_TEMPLATES = (
    "Hello. {name} is {role} in the {department_name}.",
    "Hi. {name} works as {role} in the {department_name}.",
    "Certainly. {name} is part of the {department_name} as {role}.",
)
