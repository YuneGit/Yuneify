import random
import reapy
from reapy import reascript_api as RPR

class ScriptOperations:
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

    def execute(self, script):
        """Execute MIDI scripting code"""
        try:
            # Create a local namespace with REAPER API access
            local_vars = {
                'RPR': RPR,
                'reapy': reapy,
                'project': self.project,
                'take': self.get_active_take(),
                'notes': [],
                'cc': [],
                'pb': [],
                'pc': [],
                'selected_notes': [],
                'selected_cc': [],
                'selected_pb': [],
                'selected_pc': [],
                'utils': {
                    'map_value': lambda x, in_min, in_max, out_min, out_max: 
                        (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min,
                    'random_range': lambda min_val, max_val: random.uniform(min_val, max_val),
                    'scale_velocities': lambda factor: [
                        setattr(n, 'velocity', min(max(int(n.velocity * factor), 0), 127))
                        for n in local_vars['notes']
                    ]
                }
            }
            
            # Get current MIDI data
            take = local_vars['take']
            if take:
                local_vars['notes'] = take.notes
                local_vars['cc'] = take.get_cc_events()
                local_vars['pb'] = take.get_pitch_bend_events()
                local_vars['pc'] = take.get_program_change_events()
                
                # Get selected events
                local_vars['selected_notes'] = [n for n in local_vars['notes'] if n.selected]
                local_vars['selected_cc'] = [c for c in local_vars['cc'] if c.selected]
                local_vars['selected_pb'] = [p for p in local_vars['pb'] if p.selected]
                local_vars['selected_pc'] = [p for p in local_vars['pc'] if p.selected]

            # Start undo block
            RPR.Undo_BeginBlock2(take.id)

            # Execute the script
            exec(script, globals(), local_vars)
            
            # Commit changes
            if take:
                RPR.MIDI_Sort(take.id)
            
            # End undo block
            RPR.Undo_EndBlock2(take.id, "Execute MIDI Script", -1)
            
            print("Script executed successfully.")
            
        except Exception as e:
            print(f"Error executing script: {str(e)}")
            print("Script execution failed. Changes have been rolled back.")
            if take:
                RPR.Undo_DoUndo2(take.id)  # Rollback changes on error
            raise
