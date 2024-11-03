# Maintainer's guide

## Setup

- Install `uv` (<https://docs.astral.sh/uv/>).

## Build

- Use `uv` to run the default `nox` session:

      uv run nox

  Or specify this `run` session directly:

      uv run nox -s run

## Perform checks

- Run the `nox` session `check` to perform linting, type checking, and to run
  tests:

      uv run nox -s check
