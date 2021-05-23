import math

import cudf
import numpy as np

from be.utils import gauss, calculate_diagonal_square_of_side


def set_transparency_gaussian(x, transparency, mean, std, min_out=0, max_out=1):
    for i, length in enumerate(x):
        transparency[i] = gauss(length, mean, std, min_out, max_out)

class TransparencyCalculator:

    def __init__(self, graph_side, configurations):
        """

        :param graph_side: graph space coordinates
        :param longest_edge: graph space coordinates
        :param configurations:
        """
        self.graph_side = graph_side
        self.tile_size = configurations['tile_size']
        self.zoom_levels = configurations['zoom_levels']
        self.std = configurations['std_transparency_as_percentage']
        self.tile_based_mean = configurations["tile_based_mean_transparency"]
        self.min_t = configurations['min_transparency']
        self.max_t = configurations['max_transparency']

    def calculate_edge_transparencies(self, edge_lengths):
        longest_theoretical_edge = calculate_diagonal_square_of_side(self.graph_side)
        if math.floor(max(edge_lengths)) > longest_theoretical_edge:
            raise Exception(
                "You are trying to estimate the transparency of an edge that is longer than the diagonal of the \n"
                "square into which the graph is enclosed, the side of the square is {0} but there is an edge that is \n"
                "{1} , the max length is {2}".format(self.graph_side, max(edge_lengths), longest_theoretical_edge))

        transparencies = {}
        for zl in range(0, self.zoom_levels):
            mean_graph_space = self.graph_side * (self.tile_based_mean / (2 ** zl))
            std_graph_space = self.graph_side * (self.std / (2 ** zl))

            frame = cudf.DataFrame(edge_lengths, columns=['x'])
            trans = frame.apply_rows(set_transparency_gaussian,
                                     incols=['x'],
                                     outcols=dict(transparency=np.float64),
                                    kwargs={'mean': mean_graph_space,
                                            'std': std_graph_space,
                                            'min_out': self.min_t,
                                            'max_out': self.max_t})
            transparencies[zl] = trans.to_pandas()['transparency']

        return transparencies



