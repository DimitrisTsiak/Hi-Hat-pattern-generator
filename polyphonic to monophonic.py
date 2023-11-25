import os
import mido

def polyphonic_to_monophonic(input_file, output_file):
    midi = mido.MidiFile(input_file)
    output_midi = mido.MidiFile()

    # Create a new track for the monophonic output
    output_track = mido.MidiTrack()
    output_midi.tracks.append(output_track)

    # Keep track of the currently playing notes
    active_notes = {}

    # Iterate through each track
    for track in midi.tracks:
        for msg in track:
            if msg.type == 'note_on' and msg.velocity > 0:
                # Add the note to the active_notes dictionary
                active_notes[msg.note] = msg.velocity

                # Create a new message for the note with the lowest pitch
                min_note = min(active_notes, key=active_notes.get)
                new_msg = mido.Message('note_on', note=min_note, velocity=msg.velocity, time=msg.time)
                output_track.append(new_msg)

            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                # Remove the note from the active_notes dictionary
                active_notes.pop(msg.note, None)

                # Create a new message for the note with the lowest pitch
                min_note = min(active_notes, key=active_notes.get) if active_notes else None
                new_msg = mido.Message('note_off', note=min_note, velocity=msg.velocity, time=msg.time)
                output_track.append(new_msg)

    # Save the monophonic MIDI file
    output_midi.save(output_file)

def process_folder(input_folder, output_folder):
    for filename in os.listdir(input_folder):
        if filename.endswith(".mid"):
            input_file = os.path.join(input_folder, filename)
            output_file = os.path.join(output_folder, filename)
            polyphonic_to_monophonic(input_file, output_file)

input_folder = "hi_hat_midis"
output_folder = "hi_hat_midis_monophonic"
process_folder(input_folder, output_folder)



