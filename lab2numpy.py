from utils import ChordReader
import numpy as np


def process_features(available_data, mode='simple'):
    cr = ChordReader(mode)
    for album, song in available_data:
        print('Processing album {} song {} ...'.format(album, song))
        for pitch in [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6]:
            array = cr(album, song, pitch)
            np.save('./data/labels/{}_{}_{}.npy'.format(album, song, pitch), array)


if __name__ == '__main__':
    data = [('01', '01'), ('01', '02'), ('01', '03'), ('01', '04'), ('01', '05'), ('01', '06'), ('01', '07'),
            ('01', '08'), ('01', '09'), ('01', '10'), ('01', '11'), ('01', '12'), ('01', '13'), ('01', '14'),
            ('02', '01'), ('02', '02'), ('02', '03'), ('02', '04'), ('02', '06'), ('02', '07'), ('02', '08'),
            ('02', '09'), ('02', '10'), ('02', '11'), ('02', '12'), ('02', '14'),
            ('03', '01'), ('03', '02'), ('03', '03'), ('03', '04'), ('03', '05'), ('03', '06'), ('03', '07'),
            ('03', '08'), ('03', '09'), ('03', '10'), ('03', '11'), ('03', '12'), ('03', '13'),
            ('06', '01'), ('06', '02'), ('06', '03'), ('06', '04'), ('06', '05'), ('06', '06'), ('06', '07'),
            ('06', '08'), ('06', '09'), ('06', '10'), ('06', '11'), ('06', '12'), ('06', '13'), ('06', '14'),
            ('07', '01'), ('07', '02'), ('07', '03'), ('07', '04'), ('07', '05'), ('07', '06'), ('07', '07'),
            ('07', '08'), ('07', '09'), ('07', '10'), ('07', '11'), ('07', '12'), ('07', '13'), ('07', '14'),
            ('12', '01'), ('12', '02'), ('12', '03'), ('12', '04'), ('12', '05'), ('12', '06'), ('12', '07'),
            ('12', '08'), ('12', '09'), ('12', '10'), ('12', '11'), ('12', '12')]
    process_features(data)
