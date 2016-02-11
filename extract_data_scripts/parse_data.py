import os, csv, sys, hdf5_getters

"""
The purpose of this script is to parse and extract
metadata of more than 1M songs provided in HDF5
format.

Inspired by https://github.com/tbertinmahieux/MSongsDB/blob/master/PythonSrc/hdf5_getters.py

"""


if __name__ == '__main__':
	""" MAIN """

	# get params
	hdf5path = sys.argv[1]
	songidx = 0

	song_metadata = open("song_details.txt", "w+")

	with open('song_list.csv', mode='r') as infile:
		reader = csv.reader(infile)
		song_dict = {rows[1]:int(rows[0]) for rows in reader}

	ids = max(song_dict.values())

	# sanity check
	for root, dirs, files in os.walk(hdf5path):
		str_to_write = ""
		for filed in files:
			h5 = hdf5_getters.open_h5_file_read(root+"/"+filed)

			# get all getters
			keys_to_extract = ["get_song_id","get_title", "get_track_id", "get_artist_id", "get_artist_name", "get_duration", "get_year", "get_artist_location", "get_artist_familiarity", "get_artist_hotttnesss", "get_loudness"]
			getters = filter(lambda x: x[:4] == 'get_', hdf5_getters.__dict__.keys())
			getters.remove("get_num_songs") # special case
			
			getters = list(set(getters).intersection(set(keys_to_extract)))
			getters.sort(key=lambda x: keys_to_extract.index(x))

			# write extracted data to file
			csvstring = []
			for getter in getters:
				try:
					res = hdf5_getters.__getattribute__(getter)(h5,songidx)

					if getter == "get_song_id":
						if res in song_dict:
							song_numeric_id = song_dict[res]
						else:
							ids += 1
							song_numeric_id = song_dict[res] = ids

						csvstring.append(song_numeric_id)

				except AttributeError, e:
					continue
				if res.__class__.__name__ == 'ndarray':
					continue

				else:   
					csvstring.append(res)

			# write song metadata to file; separate each attribute with |
			str_to_write += "|".join([str(x) for x in csvstring]) + "\n"
			h5.close()
		song_metadata.write(str_to_write)

	song_metadata.close()
