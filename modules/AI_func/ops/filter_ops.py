import reapy
from reapy import reascript_api as RPR

class FilterOperations:
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

    def apply_filters(self, event_types, min_val, max_val):
        """Filter MIDI events based on criteria"""
        take = self.get_active_take()
        if not take:
            return

        # Get all MIDI events
        all_events = take.get_events()
        
        # Filter by event type
        filtered_events = []
        for evt in all_events:
            if isinstance(evt, reapy.Note) and "Notes" in event_types:
                if min_val <= evt.velocity <= max_val:
                    filtered_events.append(evt)
            elif isinstance(evt, reapy.CC) and "CC" in event_types:
                if min_val <= evt.cc_value <= max_val:
                    filtered_events.append(evt)
            elif isinstance(evt, reapy.PitchBend) and "Pitch Bend" in event_types:
                if min_val <= evt.value <= max_val:
                    filtered_events.append(evt)
            elif isinstance(evt, reapy.ProgramChange) and "Program Change" in event_types:
                if min_val <= evt.program <= max_val:
                    filtered_events.append(evt)

        print(f"Filtered to {len(filtered_events)} events matching criteria.")
        
        # Select only the filtered events
        RPR.MIDI_SelectAll(take.id, False)  # Deselect all first
        for evt in filtered_events:
            if isinstance(evt, reapy.Note):
                RPR.MIDI_SetNote(
                    take.id,
                    evt.index,
                    True,  # Selected
                    evt.muted,
                    evt.start,
                    evt.end,
                    evt.channel,
                    evt.pitch,
                    evt.velocity,
                    False
                )
            elif isinstance(evt, reapy.CC):
                RPR.MIDI_SetCC(
                    take.id,
                    evt.index,
                    True,  # Selected
                    evt.muted,
                    evt.position,
                    evt.channel,
                    evt.cc_number,
                    evt.cc_value,
                    False
                )
            elif isinstance(evt, reapy.PitchBend):
                RPR.MIDI_SetPitchBend(
                    take.id,
                    evt.index,
                    True,  # Selected
                    evt.muted,
                    evt.position,
                    evt.channel,
                    evt.value,
                    False
                )
            elif isinstance(evt, reapy.ProgramChange):
                RPR.MIDI_SetProgramChange(
                    take.id,
                    evt.index,
                    True,  # Selected
                    evt.muted,
                    evt.position,
                    evt.channel,
                    evt.program,
                    False
                )

        print(f"Selected {len(filtered_events)} events matching filter criteria.")
