# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.

from page.distribution.datasets import datasets
from page.distribution.eval_tasks import eval_tasks
from page.distribution.models import models
from page.distribution.scoring_functions import scoring_functions
from page.distribution.shields import shields
from page.distribution.vector_dbs import vector_dbs

from streamlit_option_menu import option_menu


def resources_page():
    options = [
        "Models",
        "Vector Databases",
        "Shields",
        "Scoring Functions",
        "Datasets",
        "Eval Tasks",
    ]
    icons = ["magic", "memory", "shield", "file-bar-graph", "database", "list-task"]
    selected_resource = option_menu(
        None,
        options,
        icons=icons,
        orientation="horizontal",
        styles={
            "nav-link": {
                "font-size": "12px",
            },
        },
    )
    if selected_resource == "Eval Tasks":
        eval_tasks()
    elif selected_resource == "Vector Databases":
        vector_dbs()
    elif selected_resource == "Datasets":
        datasets()
    elif selected_resource == "Models":
        models()
    elif selected_resource == "Scoring Functions":
        scoring_functions()
    elif selected_resource == "Shields":
        shields()


resources_page()
