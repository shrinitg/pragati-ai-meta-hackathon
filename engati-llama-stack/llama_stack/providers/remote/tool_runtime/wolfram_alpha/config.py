# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.

from typing import Optional

from pydantic import BaseModel


class WolframAlphaToolConfig(BaseModel):
    """Configuration for WolframAlpha Tool Runtime"""

    api_key: Optional[str] = None
