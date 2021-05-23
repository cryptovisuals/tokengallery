#!/usr/bin/env python
import getopt, sys, os

# -n "experiment number 7" -csv="path/to/file" -ts=512 -z=3 -min_t=0.01 -max_t=0.1 -std=0.5 -max_edge_thickness=8 -min_edge_thickness=1
from be.configuration import CONFIGURATIONS
from be.tile_creator.main import main


def extract_arguments():
    global arguments, values
    # Get full command-line arguments
    full_cmd_arguments = sys.argv
    # Keep all but the first
    argument_list = full_cmd_arguments[1:]
    print(argument_list)
    short_options = "n:z:"
    long_options = ["csv=", "labels=", "ts=", "min_t=", "max_t=", "std=", "med_thick=", "max_thick=", "med_size=",
                    "max_size=", "curvature=", "mean_t="]
    try:
        arguments, values = getopt.getopt(argument_list, short_options, long_options)
    except getopt.error as err:
        # Output error, and return with an error code
        print(str(err))
        sys.exit(2)
    return dict(arguments)


def get_cwd():
    this_file_dir = os.path.dirname(os.path.realpath(__file__))
    return this_file_dir


def result_in_directory_existing(path):
    if not os.path.exists(path):
        os.mkdir(path)


def ensure_container_directory_exists():
    result_in_directory_existing(CONFIGURATIONS['graphs_home'])


def mkdir_for_this_graph(graph_name):
    # TODO load confoguraitons instead of relying on BE
    path = os.path.join(CONFIGURATIONS['graphs_home'])
    path = os.path.join(path, graph_name)
    result_in_directory_existing(path)
    return path

# default value as second arg og 'get'
# TODO find a way of ensuring that htis dict keys are the same as defined in configuration.json
def get_final_configurations(args, graph_path, graph_name):
    configurations = {
        "output_folder": graph_path,
        'graph_name': graph_name,
        "tile_size": int(args.get('--ts', 256)),
        "zoom_levels": int(args.get('-z', 2)),
        "min_transparency": float(args.get('--min_t', 0)),
        "max_transparency": float(args.get('--max_t', 0.1)),
        "tile_based_mean_transparency": float(args.get('--mean_t', 0.5)),
        "std_transparency_as_percentage": float(args.get("--std", 0.25)),
        "max_edge_thickness": float(args.get('--max_thick', 2)),
        "med_edge_thickness": float(args.get('--med_thick', 0.25)),
        "max_vertex_size": float(args.get("--max_size", 10)),
        "med_vertex_size": float(args.get("--med_size", 0.5)),
        "curvature": float(args.get("--curvature", 0.1)),
        "bg_color": "black",
        "source": args['--csv'],
        "labels": args.get('--labels', None)
    }
    return configurations


if __name__ == "__main__":
    args = extract_arguments()
    ensure_container_directory_exists()
    graph_name = args["-n"]
    graph_path = mkdir_for_this_graph(graph_name)

    # default value as second arg og 'get'
    # TODO find a way of ensuring that htis dict keys are the same as defined in configuration.json
    configurations = get_final_configurations(args, graph_path, graph_name)
    main(configurations)
