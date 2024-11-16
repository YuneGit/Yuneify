import os
import reapy
from reapy.core.reaper import reaper
import re
from reapy.core.reaper.reaper import get_resource_path

def get_vst_plugins():
    # Get REAPER's resource path
    resource_path = get_resource_path()

    # Define paths to VST plugin files
    vst_files = [
        os.path.join(resource_path, 'reaper-vstplugins64.ini'),
        os.path.join(resource_path, 'reaper-vstplugins.ini')
    ]
    
    # Define a blacklist of entries to exclude
    blacklist = {
        "Abbey Road One  64 Bit .Vst3", "Opus.Vst3", "Bite.Vst3", "Lx480 V4.Vst3", "Fm8.Vst3","Choral.Vst3", "Dune3.Vst3", "Dirt.Vst3", "Diva X64 .Vst3", "Dpmeter5.Dll", "Dpmeter5.Vst3", "Driver.Vst3", "Dune 3.Dll", "Flair.Vst3", "Fm8.Vst3<1168312232", "Fm8.Vst3<1921331554", "Freak.Vst3", "Ga Classics Clean.Vst3", "Ga Classics Crunch.Vst3", "Ga Classics Drive.Vst3", "Ga Classics Lead.Vst3", "Guitar Rig 6.Vst3", "Guitar Rig 7.Vst3", "Insight 2.Dll", "Insight 2.Vst3", "Izinsight2.Dll", "Iznectar3Elements.Dll", "Izneoverb.Dll", "Izneutron4.Dll", "Izneutron4Compressor.Dll", "Izneutron4Elements.Dll", "Izneutron4Equalizer.Dll", "Izneutron4Exciter.Dll", "Izneutron4Gate.Dll", "Izneutron4Sculptor.Dll", "Izneutron4Transientshaper.Dll", "Izneutron4Unmask.Dll", "Izneutron4Visualmixer.Dll", "Izozone10Elements.Dll", "Izozoneimager2.Dll", "Izrelay.Dll", "Iztonalbalancecontrol2.Dll", "Izvinyl.Dll", "Izvocalsynth2.Dll", "Kv Element.Vst3", "Kv Elementfx.Vst3", "Manalyzer.Vst3", "Mautopan.Vst3", "Mautopitch.Vst3", "Mbitfun.Vst3", "Mccgenerator.Vst3", "Mcharmverb.Vst3", "Mcomb.Vst3", "Mcompressor.Vst3", "Mconvolutionez.Vst3", "Melodyne.Vst3", "Mequalizer.Vst3", "Mflanger.Vst3", "Mfreeformphase.Vst3", "Mfreqshifter.Vst3", "Mloudnessanalyzer.Vst3", "Mmetronome.Vst3", "Mnoisegenerator.Vst3", "Morphing Chstrip M.Vst3", "Morphing Chstrip S.Vst3", "Moscillator.Vst3", "Moscilloscope.Vst3", "Mphaser.Vst3", "Mratio.Vst3", "Mratiomb.Vst3", "Mringmodulator.Vst3", "Msaturator.Vst3", "Mspectralpan.Vst3", "Mstereoexpander.Vst3", "Mstereoscope.Vst3", "Mtremolo.Vst3", "Mvibrato.Vst3", "Mwavefolder.Vst3", "Mwaveshaper.Vst3", "Nectar 3 Elements.Dll", "Nectar 3 Elements.Vst3", "Nectar 4 Auto Level.Vst3", "Nectar 4 Backer.Vst3", "Nectar 4 Breath Control.Vst3", "Nectar 4 Compressor.Vst3", "Nectar 4 Deesser.Vst3", "Nectar 4 Delay.Vst3", "Nectar 4 Dimension.Vst3", "Nectar 4 Equalizer.Vst3", "Nectar 4 Gate.Vst3", "Nectar 4 Pitch.Vst3", "Nectar 4 Reverb.Vst3", "Nectar 4 Saturation.Vst3", "Nectar 4 Voices.Vst3", "Nectar 4.Vst3", "Neoverb.Dll", "Neoverb.Vst3", "Neutron 4 Compressor.Vst3", "Neutron 4 Elements.Vst3", "Neutron 4 Equalizer.Vst3", "Neutron 4 Exciter.Vst3", "Neutron 4 Gate.Vst3", "Neutron 4 Sculptor.Vst3", "Neutron 4 Transient Shaper.Vst3", "Neutron 4 Unmask.Vst3", "Neutron 4 Visual Mixer.Vst3", "Neutron 4.Vst3", "Omnisphere.Dll", "Omnisphere.Vst3", "Ozone 10 Elements.Vst3", "Ozone 11 Clarity.Vst3", "Ozone 11 Dynamic Eq.Vst3", "Ozone 11 Dynamics.Vst3", "Ozone 11 Equalizer.Vst3", "Ozone 11 Exciter.Vst3", "Ozone 11 Imager.Vst3", "Ozone 11 Impact.Vst3", "Ozone 11 Low End Focus.Vst3", "Ozone 11 Master Rebalance.Vst3", "Ozone 11 Match Eq.Vst3", "Ozone 11 Maximizer.Vst3", "Ozone 11 Spectral Shaper.Vst3", "Ozone 11 Stabilizer.Vst3", "Ozone 11 Vintage Compressor.Vst3", "Ozone 11 Vintage Eq.Vst3", "Ozone 11 Vintage Limiter.Vst3", "Ozone 11 Vintage Tape.Vst3", "Ozone 11.Vst3", "Ozone Imager 2.Dll", "Ozone Imager 2.Vst3", "Phasis.Vst3", "Raum.Vst3", "Reacast.Dll", "Reacomp.Dll", "Reacontrolmidi.Dll", "Readelay.Dll", "Reaeq.Dll", "Reafir.Dll", "Reagate.Dll", "Reainsert.Dll", "Reaktor 6.Vst3", "Reaktor 6.Vst3<2037952213", "Reaktor 6.Vst3<940816416", "Realimit.Dll", "Reaninjam.Dll", "Reapitch.Dll", "Reasamplomatic.Dll", "Reastream.Dll", "Reasurround.Dll", "Reasurround2.Dll", "Reasyndr.Dll", "Reasynth.Dll", "Reatune.Dll", "Reaverb.Dll", "Reaverbate.Dll", "Reavocode.Dll", "Reavoice.Dll", "Reaxcomp.Dll", "Relay.Dll", "Relay.Vst3", "Replika.Vst3", "Rev X Hall.Vst3", "Rev X Plate.Vst3", "Rev X Room.Vst3", "Rex Shared Library.Dll", "Rx 10 De Click.Vst3", "Rx 10 De Clip.Vst3", "Rx 10 De Hum.Vst3", "Rx 10 De Reverb.Vst3", "Rx 10 Repair Assistant.Vst3", "Rx 10 Voice De Noise.Vst3", "Rx 11 Breath Control.Vst3", "Rx 11 Connect.Vst3", "Rx 11 De Click.Vst3", "Rx 11 De Clip.Vst3", "Rx 11 De Crackle.Vst3", "Rx 11 De Ess.Vst3", "Rx 11 De Hum.Vst3", "Rx 11 De Plosive.Vst3", "Rx 11 De Reverb.Vst3", "Rx 11 Dialogue Isolate.Vst3", "Rx 11 Guitar De Noise.Vst3", "Rx 11 Monitor.Vst3", "Rx 11 Mouth De Click.Vst3", "Rx 11 Repair Assistant.Vst3", "Rx 11 Spectral De Noise.Vst3", "Rx 11 Spectral Editor.Vst3", "Rx 11 Voice De Noise.Vst3", "Serum X64.Dll", "Serum.Vst3", "Solid Bus Comp.Vst3", "Solid Dynamics.Vst3", "Solid Eq.Vst3", "Spectralayers.Vst3", "Supercharger.Vst3", "Tonal Balance Control 2.Dll", "Tonal Balance Control 2.Vst3", "Transient Master.Vst3", "Tx16Wx.Dll", "Tx16Wx.Vst3", "Tx16Wx.Vst3<1798562372", "Tx16Wx.Vst3<1956314460", "Ur44 Chstrip M.Vst3", "Ur44 Chstrip S.Vst3", "Ur44 Ga Classics Clean.Vst3", "Ur44 Ga Classics Crunch.Vst3", "Ur44 Ga Classics Drive.Vst3", "Ur44 Ga Classics Lead.Vst3", "Ur44 Rev X Hall.Vst3", "Ur44 Rev X Plate.Vst3", "Ur44 Rev X Room.Vst3", "Vinyl.Dll", "Vinyl.Vst3", "Vocalsynth 2.Dll", "Vocalsynth 2.Vst3", "Zebra2 X64 .Vst3", "Zebra2 X64 .Vst3<1115237199", "Zebra2 X64 .Vst3<788168239", "Zebra2 X64 .Vst3<942782582", "Zebra2 X64 .Vst3<959560201", "[Vstcache]"
    }
    
    # Collect unique plugin names, ignoring duplicates
    plugins = []  # Use a list to store tuples of (raw_name, processed_name)
    
    for vst_file in vst_files:
        if os.path.isfile(vst_file):
            with open(vst_file, 'r') as file:
                for line in file:
                    # Extract plugin name
                    plugin_name = line.split('=')[0].strip()

                    # Create a processed name (customize this formatting)
                    processed_name = plugin_name.replace("_", " ").title()  # Replace underscores and title case
                    proper_name = plugin_name.replace("___", " - ").replace("__64_Bit_", "").replace(".vst3", "").replace("_", " ").replace("  ", " ").replace("   ", " ")


                    # Check against blacklist for the processed name
                    if processed_name not in blacklist:
                        plugins.append((proper_name, processed_name))  # Append tuple of (raw, processed)
                        print(plugins)

    return sorted(plugins, key=lambda x: x[1])  # Sort by processed name

if __name__ == "__main__":
    plugins = get_vst_plugins()
    if plugins:
        plugin_list = "\n".join(f"{raw} - {processed}" for raw, processed in plugins)
        reaper.show_console_message(f"Available VST Plugins:\n{plugin_list}")
    else:
        reaper.show_console_message("No VST plugins found.")