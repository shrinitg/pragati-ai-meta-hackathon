# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.


def pytest_addoption(parser):
    parser.addoption(
        "--safety-shield",
        action="store",
        default="meta-llama/Llama-Guard-3-1B",
        help="Specify the safety shield model to use for testing",
    )


def pytest_generate_tests(metafunc):
    if "llama_guard_text_shield_id" in metafunc.fixturenames:
        metafunc.parametrize(
            "llama_guard_text_shield_id",
            [metafunc.config.getoption("--safety-shield")],
        )
