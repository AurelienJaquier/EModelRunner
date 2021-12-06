"""Builds morphology objects."""

from emodelrunner.morphology import SSCXNrnFileMorphology, ThalamusNrnFileMorphology


# Copyright 2020-2021 Blue Brain Project / EPFL

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


def get_axon_hoc(axon_hoc_path):
    """Returns string containing axon hoc to use as replacement.

    Args:
        axon_hoc_path (str): path to axon hoc file

    Returns:
        str: new axon hoc
    """
    with open(axon_hoc_path, "r", encoding="utf-8") as f:
        return f.read()


def create_morphology(morph_args, morph_type):
    """Creates the morphology object.

    Args:
        morph_args (dict): morphology-related configuration
        morph_type (str): string denoting morphology type e.g. sscx, thalamus

    Returns:
        ephys.morphologies.NrnFileMorphology: morphology object
    """
    try:
        replace_axon_hoc = get_axon_hoc(morph_args["axon_hoc_path"])
    except KeyError:
        replace_axon_hoc = None
    if morph_type == "sscx":
        morph = SSCXNrnFileMorphology(
            morph_args["morph_path"],
            do_replace_axon=morph_args["do_replace_axon"],
            replace_axon_hoc=replace_axon_hoc,
        )
    elif morph_type == "thalamus":
        morph = ThalamusNrnFileMorphology(
            morph_args["morph_path"],
            do_replace_axon=morph_args["do_replace_axon"],
            replace_axon_hoc=replace_axon_hoc,
        )
    return morph
