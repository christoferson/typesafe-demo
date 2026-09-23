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
uv run --env-file .env noul.py
uv run --env-file .env choice.py
uv run --env-file .env score.py
```

Set `UV_ENV_FILE=.env` once and plain `uv run choice.py` picks it up for the rest of the
shell session. Exporting the variable directly works too:

```sh
export TYPESAFE_API_KEY="your_api_key_here"
```

## Question types

You pass `system_one` a `state` dict holding the text and a `questions` dict of your own
labels mapped to question objects. Answers come back grouped by type on the response. Each
example file is annotated line by line — read those for the actual usage.

| Type | Arguments | Criteria | Read the answer via | Example |
| --- | --- | --- | --- | --- |
| `Noul` | `instructions` | — | `response.nouls[label].noul` | `noul.py` |
| `Choice` | `instructions`, `criteria` | dict of option name → `None` | `response.choices[label].choice` | `choice.py` |
| `Score` | `instructions`, `criteria` | ordered list, low to high | `response.scores[label].score` | `score.py` |

Questions in one call run in parallel, so batching several barely moves latency.

### Interpreting a Noul

A `Noul` answers a yes/no proposition and returns **the probability that the answer is
yes** — the verdict and the certainty in one number. It is not a scale of the thing you
asked about; `0.83` means "fairly confidently yes", not "83% severe". For graded levels,
ask a `Score` instead.

Threshold it according to your error costs: `0.5` when a yes and a no are equally cheap to
handle, higher when a false yes is expensive, lower when missing a true yes hurts more.
`noul.py` uses a three-way split and routes the ambiguous middle band to a human.

### What is on an answer

`ChoiceAnswer` and `ScoreAnswer` carry `.confidence` and `.probabilities` (the full
distribution over your options); `ScoreAnswer` adds `.legend` for the rubric. `NoulAnswer`
has only `.noul` — with two outcomes the single number already describes the whole
distribution, so a separate confidence would be redundant. None of the three return
reasoning text.

Every response also carries `.model` and `.usage`.

## Async client

`AsyncTypeSafeClient` mirrors the sync API: construct it with `async with`, and `await`
the `system_one` call. Everything else is identical.

## Configuration

Client constructor options: `api_key`, `base_url`, `model`, `retry`. Retries and timeouts
come from a `RetryPolicy(max_retries=..., backoff_max=..., timeout=...)`, which you can
set on the client or per call. The default model is `jev-latest`; list what's available
with `TypeSafeClient().models.list()`.

### Environment variables

| Variable | Default | Notes |
| --- | --- | --- |
| `TYPESAFE_API_KEY` | — | Required |
| `TYPESAFE_BASE_URL` | `https://api.typesafe.ai` | Point at a gateway if needed |
| `TYPESAFE_DEFAULT_MODEL` | `jev-latest` | |
| `TYPESAFE_LOG_LEVEL` | unset | `debug`, `info`, `warning`, `error`, `off` — read once at import |

## Errors

Invalid API keys raise `TypeSafeError` at client creation, before any request is made.
Request failures raise `TypeSafeAPIError`, which carries `.status` and `.request_id` —
both worth logging when you report a problem. Subclasses cover the specific cases:
`TypeSafeAuthenticationError`, `TypeSafeRateLimitError`, `TypeSafeAPITimeoutError`,
`TypeSafeAPIConnectionError`, and others.

## Files

| File | Purpose |
| --- | --- |
| `noul.py` | Minimal single-`Noul` example |
| `choice.py` | Minimal single-`Choice` example |
| `score.py` | Minimal single-`Score` example |
| `pyproject.toml` | Project metadata and dependencies |
| `uv.lock` | Pinned dependency versions |
