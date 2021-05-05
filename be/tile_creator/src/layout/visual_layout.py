import math

import cugraph
import numpy as np
import pandas as pd
from cuml.neighbors.nearest_neighbors import NearestNeighbors
import cudf

from be.utils import shift_and_scale, gauss


def convert_graph_coordinate_to_map(source_x, source_y, target_x, target_y, out_1, out_2, out_3, out_4,
                                    tile_size, min_coordinate, max_coordinate):
    for i, (xs, ys, xt, yt) in enumerate(zip(source_x, source_y, target_x, target_y)):
        graph_side = max_coordinate - min_coordinate
        out_1[i] = (xs + abs(max_coordinate)) * tile_size / graph_side
        out_2[i] = (ys + abs(min_coordinate)) * tile_size / graph_side
        out_3[i] = (xs + abs(max_coordinate)) * tile_size / graph_side
        out_4[i] = (ys + abs(min_coordinate)) * tile_size / graph_side


class VisualLayout:
    default_force_atlas_2_options = {'max_iter': 500,
                                     'strong_gravity_mode': False,
                                     'barnes_hut_theta': 1.2,
                                     'outbound_attraction_distribution': False,
                                     'gravity': 1,
                                     'scaling_ratio': 1}

    def __init__(self, graph, config):
        self.graph = graph

        self.vertex_positions = self._run_force_atlas_2(graph.gpu_frame)
        self.vertex_positions = self.vertex_positions.sort_values(['vertex'])
        temp_max = max(self.vertex_positions.max()['x'], self.vertex_positions.max()['y'])
        temp_min = min(self.vertex_positions.min()['x'], self.vertex_positions.min()['y'])
        self._ensure_layout_is_square(temp_min, temp_max)
        self.ids_to_graph_positions = self.make_ids_to_graph_positions()
        self.edge_lengths_graph_space = self._calculate_edge_lengths_graph_space()
        self.edge_lengths_tile_space = self.edge_lengths_graph_space * config['tile_size'] / (temp_max - temp_min)
        self.median_pixel_distance = self.compute_median_pixel_distance(config['tile_size'], temp_min, temp_max)
        self.vertex_sizes = self.calculate_vertices_size(graph.degrees['in_degree'], config['med_vertex_size'],
                                                         config['max_vertex_size'])
        log_amounts = np.log10(graph.edge_amounts['amount'].values + 1)  # amounts can be huge numbers, reduce the range
        self.edge_thickness = self.calculate_edges_thickness(log_amounts, config['med_edge_thickness'],
                                                             config['max_edge_thickness'])

        # TODO
        # noverlap

        self.min = temp_min
        self.max = temp_max

        self.edge_transparencies = {}

    def _run_force_atlas_2(self, gpu_graph):
        if not isinstance(gpu_graph, cugraph.structure.graph.Graph):
            raise TypeError("The cuGraph implementation of Force Atlas requires a gpu frame")
        # layout: x y vertex
        layout = cugraph.layout.force_atlas2(gpu_graph, **self.default_force_atlas_2_options)
        layout = layout.to_pandas()
        # layout = self._distribute_on_square_edges(layout)
        return layout

    def _distribute_on_square_edges(self, layout):
        '''
        The layout generated by fa2 is a circle but the canvas is a rectangle.
        Therefore the corners of the rectangle won't have any node.
        We rectangularise the circular layout in order to better spread out the nodes.
        '''

        def scale(array, a, b):
            return (b - a) * ((array - min(array)) / max(1, (max(array) - min(array)))) + a

        # the layout is circular # to use more of the rectangular space, project onto a square
        u = layout["x"]
        v = layout["y"]
        umax = u.max()
        umin = u.min()
        vmax = v.max()
        vmin = v.min()

        # https://stats.stackexchange.com/a/178629

        u = scale(u, -0.9, 0.9)
        v = scale(v, -0.9, 0.9)

        # https://stackoverflow.com/a/32391780
        sqrt_two = np.sqrt(2)
        x = (0.5 * np.sqrt(2 + (u * u) - (v * v) + 2 * u * sqrt_two)) - (
                0.5 * np.sqrt(2 + (u * u) - (v * v) - 2 * u * sqrt_two))
        y = (0.5 * np.sqrt(2 - (u * u) + (v * v) + 2 * v * sqrt_two)) - (
                0.5 * np.sqrt(2 - (u * u) + (v * v) - 2 * v * sqrt_two))
        # for small graphs the above equation can produce nans
        x = np.nan_to_num(x)
        y = np.nan_to_num(y)
        x = scale(x, umin, umax)
        y = scale(y, vmin, vmax)
        layout["x"] = x
        layout["y"] = y
        return layout

    def compute_median_pixel_distance(self, tile_size, min_coordinate, max_coordinate):
        tile_coordinates = self.ids_to_graph_positions.apply_rows(convert_graph_coordinate_to_map,
                                                                  incols=['source_x', 'source_y', 'target_x',
                                                                          'target_y'],
                                                                  outcols=dict(out_1=np.float64, out_2=np.float64,
                                                                               out_3=np.float64, out_4=np.float64),
                                                                  kwargs={'tile_size': tile_size,
                                                                          'min_coordinate': min_coordinate,
                                                                          'max_coordinate': max_coordinate})

        vertices_once = tile_coordinates.drop_duplicates(['source_x', 'source_y']).to_pandas()

        model = NearestNeighbors(n_neighbors=3)

        # layout = self.vertex_positions.(tuple_to_columns, axis=1).rename(columns={0: 'x', 1: 'y'})

        model.fit(vertices_once[['out_1', 'out_2']])
        distances, indices = model.kneighbors(vertices_once[['out_1', 'out_2']])
        median_pixel_distance = np.median(distances.flatten())
        return median_pixel_distance

    def _ensure_layout_is_square(self, min_coordinate, max_coordinate):
        # add two vertices that ensure that the layout is a square
        v1 = int(self.vertex_positions.max()['vertex'])
        v2 = v1 - 1

        self.vertex_positions.iloc[-1, 0:3] = [min_coordinate, min_coordinate, v1]
        self.vertex_positions.iloc[-2, 0:3] = [max_coordinate, max_coordinate, v2]

        extra = pd.DataFrame([[1, 1, v1], [1, 1, v2]], columns=['in_degreee', 'out_degree', 'vertex'])
        self.graph.degrees.append(extra)

    def calculate_vertices_size(self, in_degrees, med_vertex_size, max_vertex_size):
        target_median = self.median_pixel_distance * med_vertex_size
        target_max = self.median_pixel_distance * max_vertex_size
        return shift_and_scale(in_degrees, target_median, target_max)

    def calculate_edges_thickness(self, amounts, med_edge_thickness, max_edge_thickness):
        target_median = self.median_pixel_distance * med_edge_thickness
        target_max = self.median_pixel_distance * max_edge_thickness
        return shift_and_scale(amounts, target_median, target_max)

    def _calculate_edge_lengths_graph_space(self):
        distances = ((self.ids_to_graph_positions['source_x'] - self.ids_to_graph_positions['target_x']) ** 2 + (
                self.ids_to_graph_positions['source_y'] - self.ids_to_graph_positions['target_y']) ** 2) ** 0.5
        return distances.to_array()

    def make_ids_to_graph_positions(self):
        vertex_x_y = cudf.from_pandas(self.vertex_positions)
        vertex_x_y = vertex_x_y.rename(columns={'x': 'source_x', 'y': 'source_y'})
        graph_positions = self.graph.edge_ids_cudf.merge(vertex_x_y, left_on=['source_id'], right_on=['vertex'])
        vertex_x_y = vertex_x_y.rename(columns={'source_x': 'target_x', 'source_y': 'target_y'})
        graph_positions = graph_positions.merge(vertex_x_y, left_on=['target_id'], right_on=['vertex'])
        graph_positions = graph_positions.drop(columns=['vertex_x', 'vertex_y'])
        return graph_positions
