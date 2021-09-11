#!/usr/bin/env python3
import getopt, sys, os
os.environ["FLASK_ENV"] = "development"
sys.path.append(os.path.abspath('..'))
os.chdir(os.path.abspath(".."))
from be.tile_creator.main import main


def extractArguments():
    global arguments, values
    fullCmdArguments = sys.argv
    argumentList = fullCmdArguments[1:]
    print(argumentList)
    shortOptions = "n:z:"
    longOptions = ["csv=", "labels=", "ts=", "min_t=", "max_t=", "std=", "med_thick=", "max_thick=", "med_size=",
                    "max_size=", "curvature=", "mean_t="]
    try:
        arguments, values = getopt.getopt(argumentList, shortOptions, longOptions)
        print(">>> ", arguments)
    except getopt.error as err:
        # Output error, and return with an error code
        print(str(err))
        sys.exit(2)
    return dict(arguments)


def getCwd():
    thisFileDir = os.path.dirname(os.path.realpath(__file__))
    return thisFileDir

# default value as second arg of 'get'
# TODO find a way of ensuring that htis dict keys are the same as defined in configuration.json
def getFinalConfigurations(args, graph_name):
    configurations = {
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
        "bg_color": "grey",
        "source": args['--csv'],
        "labels": args.get('--labels', None)
    }
    return configurations


if __name__ == "__main__":
    args = extractArguments()

    # graph names should be lower case and don't contain spaces
    graph_name = args["-n"].lower().strip()
    graph_name = '_'.join(graph_name.split(' '))

    configurations = getFinalConfigurations(args, graph_name)
    main(configurations)