"""Creates .hoc from cell."""
import argparse
import json
import os

from emodelrunner.load import (
    load_sscx_config,
    get_release_params,
    get_syn_mech_args,
    # get_syn_prot_args,
    get_hoc_paths_args,
    # get_step_prot_args,
)
from emodelrunner.create_cells import create_cell_using_config
from emodelrunner.create_hoc_tools import (
    create_synapse_hoc,
    create_simul_hoc,
    create_run_hoc,
)


def write_hoc(hoc_dir, hoc_file_name, hoc):
    """Write hoc file.

    Args:
        hoc_dir (str): directory to write the file in
        hoc_file_name (str): name to give to the file
        hoc (str): content of the file
    """
    hoc_path = os.path.join(hoc_dir, hoc_file_name)
    with open(hoc_path, "w", encoding="utf-8") as hoc_file:
        hoc_file.write(hoc)


def write_hocs(hoc_paths, cell_hoc, simul_hoc, run_hoc, syn_hoc=None):
    """Write hoc files.

    Args:
        hoc_paths (dict): contains paths of the hoc files to be created
            See load.get_hoc_paths_args for details
        cell_hoc (str): content of the cell template hoc file
        simul_hoc (str): content of the 'create simulation' hoc file
        run_hoc (str): content of the hoc file meant to run the simulation
        syn_hoc (str): content of the synapses template hoc file
    """
    # cell hoc
    write_hoc(hoc_paths["hoc_dir"], hoc_paths["cell_hoc_filename"], cell_hoc)

    # createsimulation.hoc
    write_hoc(hoc_paths["hoc_dir"], hoc_paths["simul_hoc_filename"], simul_hoc)

    # run.hoc
    write_hoc(hoc_paths["hoc_dir"], hoc_paths["run_hoc_filename"], run_hoc)

    # synapses hoc
    if syn_hoc is not None:
        write_hoc(hoc_paths["syn_dir"], hoc_paths["syn_hoc_filename"], syn_hoc)


def get_hoc(config):
    """Return the hoc scripts as strings.

    Args:
        config (configparser.ConfigParser): configuration

    Returns:
        (str, str, str, str): cell_hoc, syn_hoc, simul_hoc, run_hoc

        the hoc scripts for the cell, the synapses, the simulation and the run_launcher.
        syn_hoc is None if the synapses were not added
    """
    # pylint: disable=too-many-locals
    # get directories and filenames from config
    cell_template_path = config.get("Paths", "cell_template_path")
    run_hoc_template_path = config.get("Paths", "run_hoc_template_path")
    createsimulation_template_path = config.get(
        "Paths", "createsimulation_template_path"
    )
    synapses_template_path = config.get("Paths", "synapses_template_path")
    add_synapses = config.getboolean("Synapses", "add_synapses")
    syn_temp_name = config.get("Synapses", "hoc_synapse_template_name")
    hoc_paths = get_hoc_paths_args(config)
    apical_point_isec = config.get("Protocol", "apical_point_isec")

    constants_args = {
        "emodel": config.get("Cell", "emodel"),
        "morph_path": config.get("Paths", "morph_path"),
        "gid": config.getint("Cell", "gid"),
        "dt": config.getfloat("Sim", "dt"),
        "celsius": config.getfloat("Cell", "celsius"),
        "v_init": config.getfloat("Cell", "v_init"),
        "mtype": config.get("Morphology", "mtype"),
    }

    # get the protocols definitions
    protocols_filename = config.get("Paths", "prot_path")
    with open(protocols_filename, "r", encoding="utf-8") as protocol_file:
        protocol_definitions = json.load(protocol_file)
    if "__comment" in protocol_definitions:
        del protocol_definitions["__comment"]

    # get cell
    cell = create_cell_using_config(config)
    release_params = get_release_params(config)

    # get cell hoc
    cell_hoc = cell.create_custom_hoc(
        release_params,
        template_path=cell_template_path,
        syn_dir=hoc_paths["syn_dir_for_hoc"],
        syn_hoc_filename=hoc_paths["syn_hoc_filename"],
        syn_temp_name=syn_temp_name,
    )

    simul_hoc, n_stims = create_simul_hoc(
        template_path=createsimulation_template_path,
        add_synapses=add_synapses,
        hoc_paths=hoc_paths,
        constants_args=constants_args,
        protocol_definitions=protocol_definitions,
        apical_point_isec=apical_point_isec,
    )

    run_hoc = create_run_hoc(
        template_path=run_hoc_template_path,
        n_stims=n_stims,
    )

    # get synapse hoc
    if cell.add_synapses:
        # load synapse config data
        syn_mech_args = get_syn_mech_args(config)

        # get synapse hoc
        syn_hoc = create_synapse_hoc(
            syn_mech_args=syn_mech_args,
            syn_hoc_dir=hoc_paths["syn_dir_for_hoc"],
            template_path=synapses_template_path,
            gid=cell.gid,
            dt=constants_args["dt"],
            synapses_template_name=syn_temp_name,
        )
    else:
        syn_hoc = None

    return cell_hoc, syn_hoc, simul_hoc, run_hoc


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config_path",
        default=None,
        help="the path to the config file.",
    )
    args = parser.parse_args()

    config_ = load_sscx_config(config_path=args.config_path)

    cell_hoc_, syn_hoc_, simul_hoc_, run_hoc_ = get_hoc(config=config_)

    hoc_paths_ = get_hoc_paths_args(config_)
    write_hocs(
        hoc_paths_,
        cell_hoc_,
        simul_hoc_,
        run_hoc_,
        syn_hoc_,
    )
