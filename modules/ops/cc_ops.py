import reapy
from reapy import reascript_api as RPR

class CCOperations:
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

    def apply_curve(self, cc_num, curve_points):
        """Apply CC curve to selected events"""
        take = self.get_active_take()
        if not take:
            return

        # Get all CC events for the specified CC number
        cc_events = [evt for evt in take.get_cc_events() 
                    if evt.cc_number == cc_num]
        
        if not cc_events:
            print(f"No CC{cc_num} events found.")
            return

        print(f"Applying curve to {len(cc_events)} CC{cc_num} events.")
        
        # Normalize curve points to 0-1 range
        x_vals = [p[0] for p in curve_points]
        y_vals = [p[1] for p in curve_points]
        x_min, x_max = min(x_vals), max(x_vals)
        y_min, y_max = min(y_vals), max(y_vals)
        
        # Create interpolation function
        x_normalized = [(x - x_min) / (x_max - x_min) for x in x_vals]
        y_normalized = [(y - y_min) / (y_max - y_min) for y in y_vals]
        
        # Apply curve to each CC event
        for evt in cc_events:
            # Get normalized position in time
            pos = evt.position / take.length
            
            # Find closest curve points
            prev_idx = 0
            while prev_idx < len(x_normalized) - 1 and x_normalized[prev_idx + 1] < pos:
                prev_idx += 1
                
            if prev_idx >= len(x_normalized) - 1:
                new_value = y_normalized[-1]
            else:
                # Linear interpolation between points
                x0, x1 = x_normalized[prev_idx], x_normalized[prev_idx + 1]
                y0, y1 = y_normalized[prev_idx], y_normalized[prev_idx + 1]
                new_value = y0 + (y1 - y0) * (pos - x0) / (x1 - x0)
            
            # Scale back to 0-127 range
            new_cc_value = int(new_value * 127)
            new_cc_value = min(max(new_cc_value, 0), 127)
            
            # Update CC event
            RPR.MIDI_SetCC(
                take.id,
                evt.index,
                evt.selected,
                evt.muted,
                evt.position,
                evt.channel,
                evt.cc_number,
                new_cc_value,
                False
            )
            print(f"Updated CC{cc_num} at position {evt.position} to value {new_cc_value}.")
