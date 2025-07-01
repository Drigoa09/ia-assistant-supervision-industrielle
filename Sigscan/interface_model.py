from interface_model_folder.positions import Position_Format
from interface_model_folder.zone import Zone_Format

from typing import List

import numpy as np

class inferface_model:

    def __init__(self, nb_frames_total, zones : List[Zone_Format], objet_positions : dict[str, List[Position_Format]]):
        self.nb_frames_total = nb_frames_total
        self.zones = zones
        self.objet_positions = objet_positions

    def get_positions(self, time : int):

        objets = {}
        
        for positions in self.objet_positions:

            positions_futures = [position for position in positions if position.date > time]

            date_index = np.argmin(diff_dates)

            if date_index < n:
                ratio = diff_dates / (dates[date_index + 1] - dates[date_index])

