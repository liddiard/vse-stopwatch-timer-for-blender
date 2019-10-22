########################### BEGIN GPL LICENSE BLOCK ###########################
#
#     VIDEO SEQUENCE EDITOR STOPWATCH & TIMER FOR BLENDER
#     Copyright (C) 2017 Mike Meyers 
#
#     This program is free software; you can redistribute it and/or
#     modify it under the terms of the GNU General Public License as 
#     published by the Free Software Foundation; either version 3 
#     of the License, or (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#     
#     You should have received a copy of the GNU General Public License
#     along with this program; if not, write to the Free Software Foundation,
#     Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
############################ END GPL LICENSE BLOCK ############################

#________________________________<[ CREDITS ]>_________________________________
#
# "secondsToStr()" function was provided by Paul McGuire under the CC BY-SA 4.0 
# Currently, the "CC BY-SA 4.0" License is "one way" compatible with the GPL 3 
# Link to Paul McGuire's secondsToStr() function:
# https://goo.gl/hTzJYM
# Link to Paul McGuire's stackoverflow.com profile:
# http://stackoverflow.com/users/165216/paul-mcguire
#
# All other code written by Mike Meyers
#______________________________________________________________________________

#____________________________<[ SUPPORT \ CONTACT ]>___________________________
#
# Programmed by Mike "Mikeycal" Meyers
# Website: http://www.mikeycal.com
# Blender Video Editing Tutorials: https://www.youtube.com/user/MikeycalDOTcom
# Support Email [Paypal Donations Email] : mikeycaldotcom@yahoo.com
#______________________________________________________________________________

#______________________________<[ INSTRUCTIONS ]>______________________________
#
# SOURCE LOCATION: https://github.com/mikeycal/vse-stopwatch-timer-for-blender
#
# 1) Set the [ User Preferences ] in this script
# 2) Open Blender -> Switch any Blender Window to "Text Editor"
# 3) Click "Open" (bottom of Text Editor) and select this Python File 
# 4) Set the FPS and FRAME RANGE in the Blender render properties window
# 5) Click "Run Script" (Bottom of Text Editor)
# 6) Blender will create timestamps for the length of the FRAME RANGE
# 7) If blender (Not Responding) the script is still running - wait for it. 
# 8) Issues: https://github.com/mikeycal/blender-vse-stopwatch-and-timer/issues  
#______________________________________________________________________________

import bpy
import time
from functools import reduce
import math

#---------------------------- [ USER PREFERENCES ] ----------------------------
                                                                               
count_down_to_zero = True                 # (Default: False) [True, False]    #  | False = Stopwatch (Count up, starting from zero), True = Timer (Count down to zero)             
put_in_meta_strip = True                   # (Default: True) [True, False]     #  | It's much easier to manipulate as a single Meta Strip
                                                                  
#Time Format
show_start_and_end_zero_timestamp = True   # (Default: True) [True, False]     #  | Techically, first frame should be a time > 0 but often we still want to see the zeros
show_hours = True                          # (Default: True) [True, False]
show_minutes = True                        # (Default: True) [True, False]
show_seconds = True                        # (Default: True) [True, False]
show_milliseconds = False                  # (Default: False) [True, False] 

#display milliseconds as frames - like the VSE                                 #  | This requires that show_milliseconds = True
milliseconds_to_frames = False             # (Default: False) [True, False]

#Time Color, Style, Size
font_path = None                           # replace with path to font on filesystem
time_font_size = 200                       # (Default: True) [int value] 
time_color = (1,1,1,1)                     # Default: (1,1,1,1)                #  | (Red, Green, Blue, Alpha) uses floating point color values 
shadow = False                             # (Default: False) [True, False]    
shadow_color = (0,0,0,1)                   # Default: (0,0,0,1)                #  | (Red, Green, Blue, Alpha) uses floating point color values 

#-------------------------------------------------------------------------------

font = None
if font_path is not None:
    font = bpy.data.fonts.load(font_path)

# function to convert floating point number of seconds to hh:mm:ss.sss
def secondsToStr(t):                                                           
    return "%02d:%02d:%02d.%03d" % \
        reduce(lambda ll,b : divmod(ll[0],b) + ll[1:],
            [(t*1000,),1000,60,60])

get_time = str(round(time.time(),4))                                           #  | We add time to the strip name so we can add more time sequences
found_scene = False

for scene in bpy.data.scenes:
    if not found_scene:
        scene_name = scene.name
        the_framerate = scene.render.fps / scene.render.fps_base
        hold_start = start_at_frame = scene.frame_start
        hold_end = end_frame_of_project = scene.frame_end 
        zero_start = hold_start - 1
        zero_end = hold_end + 1
        total_number_of_frames = end_frame_of_project - start_at_frame + 1  
        found_scene = True
        the_channel = 1
        try:
            for seq in scene.sequence_editor.sequences_all:                    #  | Place strips above highest strip
                if seq.channel > the_channel:
                    the_channel = seq.channel + 1
        except AttributeError:                                                 #  | When VSE is empty, there is no Attribute , so we catch the error.
            print("VSE EMPTY")

the_time_in_secs = total_number_of_frames / the_framerate
time_per_frame = the_time_in_secs / total_number_of_frames

if show_start_and_end_zero_timestamp:
    add_project_frames = 2
    if count_down_to_zero: 
        new_time_per_frame = the_time_in_secs + time_per_frame
    else:
        new_time_per_frame = 0.0

else:
    add_project_frames = 1
    if count_down_to_zero: 
        new_time_per_frame = the_time_in_secs + time_per_frame
    else:
        new_time_per_frame = time_per_frame

seq = bpy.context.scene.sequence_editor_create()
bpy.ops.sequencer.select_all(action='DESELECT')                                #  | This prevents other strips from being put in metastrip

while start_at_frame <= (end_frame_of_project + add_project_frames):

    main_seq_name = str(start_at_frame) + get_time
    seq.sequences.new_effect(main_seq_name, type='TEXT', \
    channel=the_channel, frame_start=start_at_frame, \
    frame_end=(start_at_frame + 1))

    full_time = secondsToStr(new_time_per_frame)   

    h, m, s = full_time.split(':')
    s, ms = s.split('.')

    final_print_string = ""    

    if show_hours: 
        final_print_string += h + ":"  
    if show_minutes:
        final_print_string += m + ":" 
    if show_seconds:
        final_print_string += s
    if show_milliseconds:
        if milliseconds_to_frames:
            milliseconds_per_frame = math.floor(1000 / the_framerate) 
            ms,remainder = divmod(float(ms),milliseconds_per_frame)
            final_print_string += ":" 
            if ms <= 9:
                final_print_string += "0"
            final_print_string += str(int(ms))
            if int(h) < 0:
                final_print_string = "00:00:00:00"                             # This will make sure that we end on a 0 instead of a negative #
        else:
            final_print_string += "." + ms 
            if int(h) < 0:
                final_print_string = "00:00:00.000"                            # This will make sure that we end on a 0 instead of a negative #
                
    seq.sequences[main_seq_name].text = final_print_string
    seq.sequences[main_seq_name].font_size = time_font_size
    seq.sequences[main_seq_name].color = time_color
    seq.sequences[main_seq_name].use_shadow = shadow
    seq.sequences[main_seq_name].shadow_color = shadow_color
    if font is not None:
        seq.sequences[main_seq_name].font = font

    if count_down_to_zero: 
        new_time_per_frame = new_time_per_frame - time_per_frame               # decrement for next pass
    else:
        new_time_per_frame = new_time_per_frame + time_per_frame               # increment for next pass

    start_at_frame += 1

if put_in_meta_strip:
    bpy.ops.sequencer.meta_make()
    my_meta = bpy.context.scene.sequence_editor.active_strip.name
    for scene in bpy.data.scenes:
        scene.sequence_editor.sequences_all[my_meta].blend_type = "ALPHA_OVER"
