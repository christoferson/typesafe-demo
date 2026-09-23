from typesafe_sdk import Score, TypeSafeClient

with TypeSafeClient() as client:
    response = client.system_one(
        state={"document": "I was charged twice. Please fix this ASAP."},
        questions={
            "urgency": Score(
                instructions="How urgent is this ticket?",
                # Lowest rung first. The order is what makes this a scale rather than
                # a set of unrelated labels, so keep the steps evenly spaced.
                criteria=["can wait", "this week", "today"],
            ),
        },
    )

# .score is a float over the rung positions, so it can land between rungs - an
# expected value, not an index.
print(response.scores["urgency"].score)

# The answer also carries .confidence, .probabilities per rung, and .legend, which
# maps rung positions back to the criteria you supplied.
print(response.scores["urgency"].legend)
