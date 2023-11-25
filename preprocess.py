import os
import music21 as m21
import json
import tensorflow.keras as keras
import numpy as np
MIDI_DATASET_PATH = "hi_hat_midis"
#TRIPLETS = 0.333333333
ACCEPTABLE_DURATIONS = [0.0625, 0.125, 0.25, 0.5, 0.75, 1.0, 1.5, 2, 3, 4]
SINGLE_FILE_DATASET = "file_dataset"
SEQUENCE_LENGTH = 64
SAVE_DIR = "dataset/"
MAPPING_PATH = "mapping.json"
#kern, MIDI,MusicXML -> m2 -> kern,MIDI,...
#it not just from changin the format of data, it has a lot of tools such as keyrecognition
def load_songs_in_midi(dataset_path):
    songs = []
    #go through all the files in the dataset and load them with music21
    for path, subdirs, files in os.walk(dataset_path):
        for file in files:
            if file[-3:] == "mid":
                #song is a string in the music21 representation
                song = m21.converter.parse(os.path.join(path, file),quantizePost=False)
                song.show()
                songs.append(song)
    return songs

def has_acceptable_durations(song, acceptable_durations):
    for note in song.flat.notesAndRests:
        if note.duration.quarterLength not in acceptable_durations:
            return False
    return True
    
# def transpose(song):
#     #get key from the song 
#     parts = song.getElementsByClass(m21.stream.Part)
#     measure_part0 = parts[0].getElementsByClass(m21.stream.Measure)
#     key = measure_part0[0][4]


#     #estimate key using music21
#     if not isinstance(key, m21.key.Key):
#         key = song.analyze("key")
    
#     #print(key)

#     #transpose song by calculated interval
#     if key.mode == "major":
#         interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("C"))
#     elif key.mode == "minor":
#         interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("A"))
#     transposed_song = song.transpose(interval)

#     return transposed_song


def encode_song(song, time_step = 0.0625): 
    # it will encode it to the time series representation
    #p = 60 , d = 1.0 -> [60, "_","_","_"]
    encoded_song = []
    for event in song.flat.notesAndRests:
        symbol = None
        # handle notes
        print(event)
        if isinstance(event, m21.note.Note):
            symbol = event.pitch.midi #60
    
        elif isinstance(event, m21.note.Rest):
            symbol = "r"
        #elif isinstance(event, m21.chord.Chord):
        #    symbol = event.pitches
        #why do we use both "r" and "_" , isn't it hte same? No its not _ represents for how many timesteps the note is held
        #convert the note/rest into time series notation
        steps = int(event.duration.quarterLength / time_step)
        # i am not sure i understand this 
        for step in range(steps):
            if step == 0:
                encoded_song.append(symbol)
            else:
                encoded_song.append("_")
    #cast encoded song to a string
    encoded_song = " ".join(map(str, encoded_song))
    return encoded_song

def preprocess(dataset_path):
    #pass

    #load the folk songs
    print("loading songs..")
    songs = load_songs_in_midi(dataset_path)
    print(f"loaded{len(songs)} songs.")
    k = 0
    l = 0

    #filter out songs that have not acceptable durations
    #triplets etc..
    for i, song in enumerate(songs):
        #filter out songs that have not acceptable durations
        #triplets etc..
        if not has_acceptable_durations(song, ACCEPTABLE_DURATIONS):
            k += 1
            continue
        l += 1

        #transpoce songs to cmajor or a minor
        #song = transpose(song)

        #whst hsppens   if not in scale?

        #encode songs with music time series representation
        encoded_song = encode_song(song)
        #save songs to text file
        save_path = os.path.join(SAVE_DIR, str(i))
        with open(save_path, "w") as fp:
            fp.write(encoded_song)
    print(f"dataset had {l} acceptable midis and {k} non accepted")

def load(file_path):
    with open(file_path, "r") as fp:
        song = fp.read()
    return song

def  create_single_file_dataset(dataset_path, file_dataset_path, sequence_length):
    new_song_delimiter = "/ " * sequence_length
    songs = ""  
    #load encoded songs and add delimiters
    for path, _, files in os.walk(dataset_path):
        for file in files:
            file_path = os.path.join(path, file)
            song = load(file_path)
            songs = songs + song + " " + new_song_delimiter
    song = songs[:-1]

    #save string that contains all dataset
    with open(file_dataset_path, "w") as fp:
        fp.write(songs)
    return songs
def create_mapping(songs, mapping_path):
    mappings = {}

    # identify the vocabulary
    songs = songs.split()
    vocabulary = list(set(songs))
    # create a mapping
    for i, symbol in enumerate(vocabulary):
        mappings[symbol] = i
    #save a vocabulary to a json file
    with open(mapping_path, "w") as fp:
        json.dump(mappings, fp, indent=4)

def convert_songs_to_int(songs):
    #we want to map our song dataset to integers
    int_songs=[]
    #load_mappings
    with open(MAPPING_PATH, "r") as fp:
        mappings = json.load(fp)

    #cast songs string to a list
    songs = songs.split()

    #map songs to int
    for symbol in songs:
        int_songs.append(mappings[symbol])
    
    return int_songs

def generate_training_sequences(sequence_length):
    # [11,12,13,14,...] -> i:[11,12], t:13;i[12, 13],t:14
    
    #load the songs and map them to int
    songs = load(SINGLE_FILE_DATASET)
    int_songs = convert_songs_to_int(songs)
    
    #generate the training sequences
    # 100 symbols, 64 length, 100-64 = 36
    inputs = []
    targets = []
    num_sequences = len(int_songs) - sequence_length
    for i in range(num_sequences):
        inputs.append(int_songs[i:i+sequence_length])
        targets.append(int_songs[i+sequence_length])

    #one hot encode the sequences
    #inputs: (#of sequences, sequence length, vocabulary_size)
    #[[0, 1, 2],[1, 1, 2]] ->  [[[1,0,0],[0,1,0],[0,0,1]],[]]
    vocabulary_size = len(set(int_songs))
    inputs = keras.utils.to_categorical(inputs, num_classes=vocabulary_size)
    targets = np.array(targets)
    return inputs, targets
    


def main():
    preprocess(MIDI_DATASET_PATH)
    songs = create_single_file_dataset(SAVE_DIR, SINGLE_FILE_DATASET, SEQUENCE_LENGTH)
    create_mapping(songs, MAPPING_PATH)
    inputs, targets = generate_training_sequences(SEQUENCE_LENGTH)
    a = 1



if __name__ == "__main__":
    main()

    
    