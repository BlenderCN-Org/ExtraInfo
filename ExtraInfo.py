import blf
import bpy

'''

    Copyright (c) 2019

    Jorge Hernández - Meléndez Saiz
    zebus3dream@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.


'''

bl_info = {
    "name": "ExtraInfo",
    "description": "Show Extra Information in Viewport",
    "author": "zebus3d",
    "version": (0, 0, 3),
    "blender": (2, 80, 0),
    "location": "View3D",
    "wiki_url": "https://github.com/zebus3d/ExtraInfo",
    "category": "3D View" 
}


font_info = {
    "font_id": 0,
    "handler": None,
}


def get_region_property(target_region, target_property):
    matched, i = False, 0
    regions = list(bpy.context.area.regions)
    region_property = None
    while not matched:
        if regions[i].type == target_region:
            region_property = getattr(regions[i], target_property)
            matched = True
        i = i+1
    
    if region_property:
        return region_property



# this is calculated every drawing pass of the viewport:
def draw_callback_px(self, context):

    display = []
    font_id = font_info["font_id"]
    
    ui_scale = bpy.context.preferences.view.ui_scale

    x_offset_aTool = bpy.context.area.regions[2].width

    if x_offset_aTool == 1:
        x_offset = 20 * ui_scale 
    else:   
        x_offset = 20 * ui_scale + x_offset_aTool

    # esto es solo en el layaout principal pero puede cambiar:
    # TOOL_HEADER = 0
    # HEADER = 1
    # TOOLS = 2
    # UI = 3
    # HUD = 4 
    # WINDOW = 5
    # por eso me hice el metodo get_region_property

    header_height = get_region_property('HEADER', 'height')
    header_y = get_region_property('HEADER', 'y')
    
    window_height = get_region_property('WINDOW', 'height')
    # window_height = get_region_property('WINDOW', 'y')
    # print("window.height", window_height)
    
    # normalize y offset:
    # ui_min = 0.5
    # ui_max = 2
    # normalize range(0.5-2) to 0-1:
    # y_normalized = (ui_scale - ui_min)/(ui_max-ui_min)
    # print(y_normalized)
    # normalize range(0.5-2) to 0-100:
    # y_normalized = (ui_scale - ui_min)/(ui_max-ui_min)*100
    # print(y_normalized)


    if header_height == 1:
        # sin header
        # size min 0:
        # y_static_offest = 35
        # size 1:
        # y_static_offest = 65
        # size 2 max:
        # y_static_offest = 130

        OldMin = 0.5
        OldMax = 2

        NewMin = 35
        NewMax = 130
        
        OldRange = (OldMax - OldMin)
        # OldValue = y_normalized
        OldValue = ui_scale

        if OldRange == 0:
            NewValue = NewMin
        else:
            NewRange = (NewMax - NewMin)  
            y_static_offest = (((OldValue - OldMin) * NewRange) / OldRange) + NewMin
    else:
        # con header
        # size min 0:
        # y_static_offest = 50
        # size 1:
        # y_static_offest = 90        
        # size 2 max:
        # y_static_offest = 180
        
        OldMin = 0.5
        OldMax = 2

        NewMin = 50
        NewMax = 180
        
        OldRange = (OldMax - OldMin)
        # OldValue = y_normalized
        OldValue = ui_scale

        if OldRange == 0:
            NewValue = NewMin
        else:
            NewRange = (NewMax - NewMin)  
            y_static_offest = (((OldValue - OldMin) * NewRange) / OldRange) + NewMin

    # print(y_static_offest)
    y_offset = window_height - y_static_offest
    # print("y_offset", y_offset)

    fontSize = int(12 * ui_scale)
    blf.size(font_id, fontSize, 72)
    
    # shadows:
    # the level has to be 3, 5 o 0
    level = 5
    r = 0.0
    g = 0.0
    b = 0.0
    a = 0.9
    
    blf.enable(font_id , blf.SHADOW )
    blf.shadow(font_id, level, r, g, b, a)
    blf.shadow_offset(font_id, 1, -1)
    
    engines = {
        'BLENDER_EEVEE' : 'Eevee',
        'BLENDER_WORKBENCH' : 'Workbench',
        'CYCLES' : 'Cycles'
    }

    re = 'Engine: ' + engines.get(bpy.context.scene.render.engine)
    display.append(re)

    view_layer = bpy.context.view_layer
    stats = bpy.context.scene.statistics(view_layer).split("|")

    if bpy.context.mode == 'OBJECT':
        ss = stats[2:5]
        ss.append(stats[-2])
        stats = ss
    elif bpy.context.mode == 'EDIT_MESH':
        ss = stats[1:6]
        stats = ss
    elif bpy.context.mode == 'SCULPT':
        ss = stats[1:4]
        ss.append(stats[-2])
        stats = ss
    else:
        stats = []

    if len(stats) > 0:
        display = display + stats

    if engines.get(bpy.context.scene.render.engine) == 'Cycles':
        area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
        space = next(space for space in area.spaces if space.type == 'VIEW_3D')
        if space.shading.type == 'RENDERED': 
            rendered = 20
        else:
            rendered = 0
    else:
        rendered = 0

    if bpy.context.space_data.overlay.show_overlays:
        if bpy.context.space_data.overlay.show_text:
            for counter, value in enumerate(display):
                # print(value)
                value = value.replace(" ","")
                value = value.replace(":",": ")
                # print(value)
                increment = (20*counter*ui_scale)
                blf.position(font_id, x_offset, y_offset-increment-rendered*ui_scale, 0)
                blf.draw(font_id, value)



def init():
    font_info["font_id"] = 0
    # run every frame
    font_info["handler"] = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, (None, None), 'WINDOW', 'POST_PIXEL')


def register():
    init()

def unregister():
    pass

if __name__ == "__main__":
    register()
