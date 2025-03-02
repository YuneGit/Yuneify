import random
import statistics
import reapy
from reapy import reascript_api as RPR

class VelocityOperations:
    def __init__(self):
        with reapy.inside_reaper():
            self.project = reapy.Project()

    def get_active_take(self):
        with reapy.inside_reaper():
            item = self.project.get_selected_item(0)
            if not item:
                print("No selected item.")
                return None

            take = item.active_take
            if not take:
                print("No active take.")
                return None

            return take

    def randomize(self, min_vel, max_vel):
        """Randomize velocities within range"""
        take = self.get_active_take()
        if not take:
            return

        notes = take.notes
        if not notes:
            print("No MIDI notes.")
            return

        print(f"Randomizing velocities for {len(notes)} notes between {min_vel}-{max_vel}.")
        for note in notes:
            new_velocity = random.randint(min_vel, max_vel)
            retval, *other_values = RPR.MIDI_GetNote(
                take.id, note.index, 0, 0, 0, 0, 0, 0, 0
            )
            muted, start, end, channel, original_pitch, _ = other_values[-6:]
            RPR.MIDI_SetNote(
                take.id,
                note.index,
                note.selected,
                muted,
                start,
                end,
                channel,
                note.pitch,
                new_velocity,
                False
            )
            print(f"Updated note (Pitch: {note.pitch}) to new velocity: {new_velocity}.")

    def normalize(self):
        """Normalize to median velocity"""
        take = self.get_active_take()
        if not take:
            return

        notes = take.notes
        if not notes:
            print("No MIDI notes.")
            return

        print(f"Normalizing velocities for {len(notes)} notes.")
        velocities = [note.velocity for note in notes]
        median_velocity = statistics.median(velocities)
        for note in notes:
            retval, *other_values = RPR.MIDI_GetNote(
                take.id, note.index, 0, 0, 0, 0, 0, 0, 0
            )
            muted, start, end, channel, original_pitch, _ = other_values[-6:]
            RPR.MIDI_SetNote(
                take.id,
                note.index,
                note.selected,
                muted,
                int(start),
                int(end),
                channel,
                note.pitch,
                int(median_velocity),
                False
            )
            print(f"Normalized note (Pitch: {note.pitch}) to median velocity: {median_velocity}.")

    def compress(self, min_vel, max_vel):
        """Compress velocity range"""
        take = self.get_active_take()
        if not take:
            return

        notes = take.notes
        if not notes:
            print("No MIDI notes.")
            return

        print(f"Compressing velocities for {len(notes)} notes to range {min_vel}-{max_vel}.")
        current_min = min(note.velocity for note in notes)
        current_max = max(note.velocity for note in notes)
        
        for note in notes:
            # Scale velocity to new range
            new_velocity = min_vel + ((note.velocity - current_min) * (max_vel - min_vel)) / (current_max - current_min)
            new_velocity = min(max(int(new_velocity), 0), 127)
            
            retval, *other_values = RPR.MIDI_GetNote(
                take.id, note.index, 0, 0, 0, 0, 0, 0, 0
            )
            muted, start, end, channel, original_pitch, _ = other_values[-6:]
            RPR.MIDI_SetNote(
                take.id,
                note.index,
                note.selected,
                muted,
                start,
                end,
                channel,
                note.pitch,
                new_velocity,
                False
            )
            print(f"Compressed note (Pitch: {note.pitch}) to velocity: {new_velocity}.")

    def scale(self, factor):
        """Scale velocities by factor"""
        take = self.get_active_take()
        if not take:
            return

        notes = take.notes
        if not notes:
            print("No MIDI notes.")
            return

        print(f"Scaling velocities for {len(notes)} notes by factor {factor}.")
        for note in notes:
            new_velocity = min(max(int(note.velocity * factor), 0), 127)
            retval, *other_values = RPR.MIDI_GetNote(
                take.id, note.index, 0, 0, 0, 0, 0, 0, 0
            )
            muted, start, end, channel, original_pitch, _ = other_values[-6:]
            RPR.MIDI_SetNote(
                take.id,
                note.index,
                note.selected,
                muted,
                start,
                end,
                channel,
                note.pitch,
                new_velocity,
                False
            )
            print(f"Scaled note (Pitch: {note.pitch}) to new velocity: {new_velocity}.")

    def adjust_velocity(self, amount):
        """Adjust selected note velocities by amount"""
        for note in self.get_selected_notes():
            new_vel = note.velocity + amount
            note.velocity = max(0, min(127, new_vel))
        self.update_notes()
