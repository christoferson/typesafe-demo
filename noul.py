from typesafe_sdk import Noul, TypeSafeClient

# A noul is the probability that the answer is yes, so these are decision
# thresholds, not severity levels. Widen the gap to send more cases to review.
NO = 0.2
YES = 0.8

with TypeSafeClient() as client:
    response = client.system_one(
        state={
            "document": (
                "Card ending 4417: $8.50 coffee in Chicago at 9:02 AM, then a $2,300 "
                "electronics purchase in Miami at 9:41 AM."
            )
        },
        questions={
            # A yes/no question needs no criteria. Phrase it so that "yes" is the
            # high end, or the thresholds below silently invert.
            "fraud": Noul(instructions="Is this card activity fraudulent?"),
        },
    )

# .noul is a float from 0 (confidently no) to 1 (confidently yes). There is no
# .confidence here - with two outcomes this number already describes the whole
# distribution.
fraud = response.nouls["fraud"].noul

# The middle band is the useful part: the model is genuinely unsure, so neither
# branch is safe to take automatically.
if fraud >= YES:
    action = "block the card"
elif fraud <= NO:
    action = "let it through"
else:
    action = "send to a human reviewer"

print(f"P(fraud) = {fraud:.2f} -> {action}")
