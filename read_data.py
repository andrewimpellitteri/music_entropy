import pickle
import os

def load_dict_from_pkl(filename):
    with open(filename, "rb") as file:
        return pickle.load(file)

def update_dict_with_file_locations(data, data_dir):
    for composer, info in data.items():
        for midi_file in info["midi_files"]:
            filename = os.path.join(data_dir, composer.replace(" ", "_"), midi_file["name"] + ".mid")
            midi_file["url"] = filename

def save_dict_to_pkl(data, filename):
    with open(filename, "wb") as file:
        pickle.dump(data, file)

# Load the pickled dictionary
composers_data = load_dict_from_pkl("composers_data.pkl")

# Update MIDI file URLs with file locations in the "data" directory
update_dict_with_file_locations(composers_data, "data/data")

print(composers_data)

# Save the updated dictionary back to a pickle file
save_dict_to_pkl(composers_data, "composers_data_updated.pkl")