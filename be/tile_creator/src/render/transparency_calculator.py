import numpy as np

class TransparencyCalculator:

    def __init__(self, min_length, max_length, configurations):
        self.configurations = configurations
        self.min_length = max(1, min_length)
        self.max_length = max_length
        self._do_args_check(max_length, min_length, self.configurations['zoom_levels'])

    def _do_args_check(self, max_length, min_length, zoom_levels):
        if min_length < 0:
            raise Exception("min_length has to be positive")
        if max_length < min_length:
            raise Exception("You need to pass min_length first and max_length second")
        if zoom_levels < 2:
            raise Exception("The minimum zoom level should be 2")

    def get_transparency(self, edge_length, zoom_level):
        if not zoom_level < self.configurations['zoom_levels'] and zoom_level > 0:
            raise Exception(
                "zoom level needs to be between 0 and the max zoom leve ({0})".format(self.configurations['zoom_levels']))
        if edge_length > self.max_length:
            raise Exception(
                "You passed an edge length longer than the maximum")

        return self.gaussian_bumps(edge_length, zoom_level)

    def gaussian_bumps(self, edge_length, zoom_level):
        '''
        A strategy to calculate transparency.
        '''

        step = (self.max_length - self.min_length) / (self.configurations['zoom_levels'] + 1)
        mean = step * (self.configurations['zoom_levels'] - zoom_level)
        std = self.configurations['std_transparency_as_percentage'] * (self.max_length - self.min_length)

        return self._gauss(edge_length, mean, std)

    def _gauss(self, x, mu, std):
        '''
        Compute gaussian function, the min outout is min_transparency, the max_output is max_transparency
        '''
        min_output = self.configurations['min_transparency']
        max_output = self.configurations['max_transparency']
        return (max_output - min_output) * np.exp(-np.power(x - mu, 2.) / (2 * np.power(std, 2.))) + min_output
