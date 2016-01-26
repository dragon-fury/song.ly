import os
import sys
import hdf5_getters
import numpy as np

if __name__ == '__main__':
	""" MAIN """

	# get params
	hdf5path = sys.argv[1]
	songidx = 0
	onegetter = ''

	csvs = open("result.csv", "w+")
	# sanity check
	for root, dirs, files in os.walk(hdf5path):
		for filed in files:
			h5 = hdf5_getters.open_h5_file_read(root+"/"+filed)
			numSongs = hdf5_getters.get_num_songs(h5)

			# get all getters
			getters = filter(lambda x: x[:4] == 'get_', hdf5_getters.__dict__.keys())
			getters.remove("get_num_songs") # special case
			need = ["get_artist_familiarity", "get_artist_hotttnesss", "get_artist_id","get_artist_name","get_duration","get_year","get_loudness","get_song_id","get_tempo","get_time_signature","get_title"]
			getters = list(set(getters).intersection(set(need)))
			getters = np.sort(getters)

			# print them
			csvstring = []
			for getter in getters:
				try:
					res = hdf5_getters.__getattribute__(getter)(h5,songidx)
				except AttributeError, e:
					continue
				if res.__class__.__name__ == 'ndarray':
					continue
				else:
					csvstring.append(res)
			csvs.write(",".join([str(x) for x in csvstring]))
			csvs.write("\n")
			h5.close()

	csvs.close()
