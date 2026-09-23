from typesafe_sdk import Choice, TypeSafeClient

with TypeSafeClient() as client:
    response = client.system_one(
        state={"document": "I was charged twice. Please fix this ASAP."},
        questions={
            "category": Choice(
                instructions="What is this ticket about?",
                # The model reads both the names and the descriptions, so a
                # description earns its keep by separating an option from its
                # neighbours rather than defining it in isolation. Pass None instead
                # where the name alone is unambiguous. Options must be mutually
                # exclusive - probabilities sum to 1 and the highest one wins.
                criteria={
                    "billing": "Charges, refunds, invoices, and payment disputes.",
                    "technical": (
                        "Bugs, errors, and broken functionality. Not charge disputes."
                    ),
                    "other": "Anything that is not billing or technical.",
                },
            ),
        },
    )

# .choice is the winning option name - always one of your criteria keys.
print(response.choices["category"].choice)

# The answer also carries the distribution behind that pick: .confidence says how
# concentrated it is, and .probabilities maps every option to its share.
print(response.choices["category"].confidence)
print(response.choices["category"].probabilities)
