# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.

import tempfile

import pytest
import pytest_asyncio

from llama_stack.apis.models import ModelInput, ModelType
from llama_stack.distribution.datatypes import Api, Provider
from llama_stack.providers.inline.agents.meta_reference import (
    MetaReferenceAgentsImplConfig,
)
from llama_stack.providers.tests.resolver import construct_stack_for_test
from llama_stack.providers.utils.kvstore.config import SqliteKVStoreConfig

from ..conftest import ProviderFixture, remote_stack_fixture


def pick_inference_model(inference_model):
    # This is not entirely satisfactory. The fixture `inference_model` can correspond to
    # multiple models when you need to run a safety model in addition to normal agent
    # inference model. We filter off the safety model by looking for "Llama-Guard"
    if isinstance(inference_model, list):
        inference_model = next(m for m in inference_model if "Llama-Guard" not in m)
        assert inference_model is not None
    return inference_model


@pytest.fixture(scope="session")
def agents_remote() -> ProviderFixture:
    return remote_stack_fixture()


@pytest.fixture(scope="session")
def agents_meta_reference() -> ProviderFixture:
    sqlite_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    return ProviderFixture(
        providers=[
            Provider(
                provider_id="meta-reference",
                provider_type="inline::meta-reference",
                config=MetaReferenceAgentsImplConfig(
                    # TODO: make this an in-memory store
                    persistence_store=SqliteKVStoreConfig(
                        db_path=sqlite_file.name,
                    ),
                ).model_dump(),
            )
        ],
    )


AGENTS_FIXTURES = ["meta_reference", "remote"]


@pytest_asyncio.fixture(scope="session")
async def agents_stack(
    request,
    inference_model,
    safety_shield,
    tool_group_input_memory,
    tool_group_input_tavily_search,
):
    fixture_dict = request.param

    providers = {}
    provider_data = {}
    for key in ["inference", "safety", "vector_io", "agents", "tool_runtime"]:
        fixture = request.getfixturevalue(f"{key}_{fixture_dict[key]}")
        providers[key] = fixture.providers
        if key == "inference":
            providers[key].append(
                Provider(
                    provider_id="agents_memory_provider",
                    provider_type="inline::sentence-transformers",
                    config={},
                )
            )
        if fixture.provider_data:
            provider_data.update(fixture.provider_data)

    inference_models = (
        inference_model if isinstance(inference_model, list) else [inference_model]
    )

    # NOTE: meta-reference provider needs 1 provider per model, lookup provider_id from provider config
    model_to_provider_id = {}
    for provider in providers["inference"]:
        if "model" in provider.config:
            model_to_provider_id[provider.config["model"]] = provider.provider_id

    models = []
    for model in inference_models:
        if model in model_to_provider_id:
            provider_id = model_to_provider_id[model]
        else:
            provider_id = providers["inference"][0].provider_id

        models.append(
            ModelInput(
                model_id=model,
                model_type=ModelType.llm,
                provider_id=provider_id,
            )
        )

    models.append(
        ModelInput(
            model_id="all-MiniLM-L6-v2",
            model_type=ModelType.embedding,
            provider_id="agents_memory_provider",
            metadata={"embedding_dimension": 384},
        )
    )

    test_stack = await construct_stack_for_test(
        [Api.agents, Api.inference, Api.safety, Api.vector_io, Api.tool_runtime],
        providers,
        provider_data,
        models=models,
        shields=[safety_shield] if safety_shield else [],
        tool_groups=[tool_group_input_memory, tool_group_input_tavily_search],
    )
    return test_stack
