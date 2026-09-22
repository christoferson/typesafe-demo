# typesafe-demo

A small demo of the [TypeSafe AI](https://typesafe.ai) Python SDK — structured, typed
classification over free text. Managed with [uv](https://docs.astral.sh/uv/).

- SDK docs: https://docs.typesafe.ai/sdk/python/
- SDK source: https://github.com/typesafe-ai/typesafe-sdk-python

## Requirements

- Python 3.13+ (see `.python-version`)
- uv
- A TypeSafe API key from [console.typesafe.ai](https://console.typesafe.ai)

## Setup

```sh
uv sync
```

To add the SDK to a fresh project:

```sh
uv add typesafe-sdk
```

Put your API key in a `.env` file at the project root:

```sh
TYPESAFE_API_KEY=your_api_key_here
```

`.env` is gitignored — never commit your key.

## Run

Python does not read `.env` automatically, so pass it to uv:

```sh
uv run --env-file .env choice.py
uv run --env-file .env score.py
```

Set `UV_ENV_FILE=.env` once and plain `uv run choice.py` picks it up for the rest of the
shell session. Exporting the variable directly works too:

```sh
export TYPESAFE_API_KEY="your_api_key_here"
```

## Example

`choice.py` asks a single `Choice` question about a support ticket:

```python
from typesafe_sdk import Choice, TypeSafeClient

with TypeSafeClient() as client:
    response = client.system_one(
        state={"document": "I was charged twice. Please fix this ASAP."},
        questions={
            "category": Choice(
                instructions="What is this ticket about?",
                criteria={"billing": None, "technical": None, "other": None},
            ),
        },
    )

print(response.choices["category"].choice)
```

## Question types

You pass `system_one` a dict of your own labels mapped to question objects. Answers come
back grouped by type on the response.

| Type | Arguments | Criteria | Read the answer via |
| --- | --- | --- | --- |
| `Noul` | `instructions` | — (returns a value in `0..1`) | `response.nouls[label].noul` |
| `Choice` | `instructions`, `criteria` | dict of option name → `None` | `response.choices[label].choice` |
| `Score` | `instructions`, `criteria` | ordered list, low to high | `response.scores[label].score` |

All three in one call:

```python
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

with TypeSafeClient() as client:
    response = client.system_one(
        state={"document": "I was charged twice. Please fix this ASAP."},
        questions={
            "billing": Noul(instructions="Is this ticket about billing?"),
            "tone": Choice(
                instructions="What is the customer's tone?",
                criteria={"calm": None, "frustrated": None, "angry": None},
            ),
            "urgency": Score(
                instructions="How urgent is this ticket?",
                criteria=["can wait", "this week", "today"],
            ),
        },
    )

print(response.nouls["billing"].noul)
print(response.choices["tone"].choice)
print(response.scores["urgency"].score)
```

## Async client

`AsyncTypeSafeClient` mirrors the sync API:

```python
import asyncio

from typesafe_sdk import AsyncTypeSafeClient, Noul


async def main() -> None:
    async with AsyncTypeSafeClient() as client:
        response = await client.system_one(
            state={"document": "I was charged twice. Please fix this ASAP."},
            questions={"billing": Noul(instructions="Is this ticket about billing?")},
        )
    print(response.nouls["billing"].noul)


asyncio.run(main())
```

## Configuration

Client constructor options: `api_key`, `base_url`, `model`, `retry`.

```python
from typesafe_sdk import RetryPolicy, TypeSafeClient

client = TypeSafeClient(
    model="jev",
    retry=RetryPolicy(max_retries=3, backoff_max=0.2, timeout=1.0),
)
```

List available models with `TypeSafeClient().models.list()`.

### Environment variables

| Variable | Default | Notes |
| --- | --- | --- |
| `TYPESAFE_API_KEY` | — | Required |
| `TYPESAFE_BASE_URL` | `https://api.typesafe.ai` | Point at a gateway if needed |
| `TYPESAFE_DEFAULT_MODEL` | `jev-latest` | |
| `TYPESAFE_LOG_LEVEL` | unset | `debug`, `info`, `warning`, `error`, `off` — read once at import |

## Errors

Invalid API keys raise `TypeSafeError` at client creation, before any request. Request
failures raise `TypeSafeAPIError`, which carries `.status` and `.request_id`:

```python
from typesafe_sdk import TypeSafeAPIError

try:
    ...
except TypeSafeAPIError as error:
    print(error.status, error.request_id)
```

## Files

| File | Purpose |
| --- | --- |
| `choice.py` | Minimal single-`Choice` example |
| `score.py` | Minimal single-`Score` example |
| `pyproject.toml` | Project metadata and dependencies |
| `uv.lock` | Pinned dependency versions |
