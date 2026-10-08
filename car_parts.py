# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import re
import math
import bpy
import bpy_extras
import mathutils
from math import inf


# ---------------------------------------------------------------------------
# Geometric & Object Helpers
# ---------------------------------------------------------------------------

def get_object_world_bounds(obj):
    """Return (min_x, max_x, min_y, max_y, min_z, max_z) in world coordinates."""
    if not obj:
        return None
    matrix = obj.matrix_world
    if hasattr(obj, 'bound_box') and obj.bound_box:
        coords = [matrix @ mathutils.Vector(p) for p in obj.bound_box]
        return (
            min(p.x for p in coords),
            max(p.x for p in coords),
            min(p.y for p in coords),
            max(p.y for p in coords),
            min(p.z for p in coords),
            max(p.z for p in coords),
        )
    loc = matrix.to_translation()
    return (loc.x - 0.5, loc.x + 0.5, loc.y - 0.5, loc.y + 0.5, loc.z - 0.5, loc.z + 0.5)


def get_object_world_center(obj):
    """Return the world space center point of the object bounding box."""
    if not obj:
        return None
    b = get_object_world_bounds(obj)
    if b:
        return mathutils.Vector(((b[0] + b[1]) / 2.0, (b[2] + b[3]) / 2.0, (b[4] + b[5]) / 2.0))
    return obj.matrix_world.to_translation()


def get_wheel_radius(obj):
    """Calculate the wheel radius from bounding box dimensions."""
    if not obj:
        return 0.4
    b = get_object_world_bounds(obj)
    if b:
        height = b[5] - b[4]
        length = b[3] - b[2]
        r = max(height, length) / 2.0
        return max(r, 0.05)
    return 0.4


def parent_object_to_bone(obj, rig, bone_name):
    """Parent an object to an armature bone while strictly preserving world transformation."""
    if not obj or not rig or not hasattr(rig, 'data') or not hasattr(rig.data, 'bones'):
        return False
    if bone_name not in rig.data.bones:
        return False

    matrix_world = obj.matrix_world.copy()
    obj.parent = rig
    obj.parent_type = 'BONE'
    obj.parent_bone = bone_name
    obj.matrix_world = matrix_world
    return True


# ---------------------------------------------------------------------------
# Smart Car Parts Auto-Detection
# ---------------------------------------------------------------------------

def detect_car_parts(context):
    """Intelligently detect Body, Wheels (FL, FR, BL, BR), and Brakes from selection or scene."""
    # First priority: currently selected mesh objects
    candidates = [o for o in context.selected_objects if o.type == 'MESH']
    if len(candidates) < 2:
        # Fallback: all visible mesh objects in scene
        candidates = [o for o in context.scene.objects if o.type == 'MESH']

    detected = {
        'body': None,
        'wheel_ft_l': None,
        'wheel_ft_r': None,
        'wheel_bk_l': None,
        'wheel_bk_r': None,
        'brake_ft_l': None,
        'brake_ft_r': None,
        'brake_bk_l': None,
        'brake_bk_r': None,
    }

    if not candidates:
        return detected

    # 1. Detect Body
    body_pattern = re.compile(r'(body|chassis|hull|frame|shell|main|cab|car_body)', re.IGNORECASE)
    for obj in candidates:
        if body_pattern.search(obj.name):
            detected['body'] = obj
            break

    # If body not identified by name, find candidate with the largest bounding box volume
    if detected['body'] is None and len(candidates) > 4:
        def obj_volume(o):
            b = get_object_world_bounds(o)
            return (b[1] - b[0]) * (b[3] - b[2]) * (b[5] - b[4]) if b else 0
        detected['body'] = max(candidates, key=obj_volume)

    remaining = [o for o in candidates if o != detected['body']]

    # 2. Detect Wheels by Name Patterns
    wheel_pattern = re.compile(r'(wheel|tire|tyre|rim)', re.IGNORECASE)
    wheel_candidates = [o for o in remaining if wheel_pattern.search(o.name)]

    # Regex patterns for wheel positions:
    # Front-Left: ft.l, front.*left, fl, l.*front
    fl_pattern = re.compile(r'(\bft[._-]?l\b|front[._-]?left|fl\b|l[._-]?front|wheel.*ft.*l)', re.IGNORECASE)
    fr_pattern = re.compile(r'(\bft[._-]?r\b|front[._-]?right|fr\b|r[._-]?front|wheel.*ft.*r)', re.IGNORECASE)
    bl_pattern = re.compile(r'(\bbk[._-]?l\b|back[._-]?left|rear[._-]?left|rl\b|bl\b|l[._-]?rear|wheel.*bk.*l)', re.IGNORECASE)
    br_pattern = re.compile(r'(\bbk[._-]?r\b|back[._-]?right|rear[._-]?right|rr\b|br\b|r[._-]?rear|wheel.*bk.*r)', re.IGNORECASE)

    for o in list(wheel_candidates):
        n = o.name
        if detected['wheel_ft_l'] is None and fl_pattern.search(n):
            detected['wheel_ft_l'] = o
        elif detected['wheel_ft_r'] is None and fr_pattern.search(n):
            detected['wheel_ft_r'] = o
        elif detected['wheel_bk_l'] is None and bl_pattern.search(n):
            detected['wheel_bk_l'] = o
        elif detected['wheel_bk_r'] is None and br_pattern.search(n):
            detected['wheel_bk_r'] = o

    # 3. Spatial Geometric Fallback for Wheels
    # If 4 wheels weren't identified by name, use spatial coordinates!
    # Rigacar coordinates: Front is -Y, Back is +Y, Left is +X, Right is -X.
    assigned_wheels = {detected['wheel_ft_l'], detected['wheel_ft_r'], detected['wheel_bk_l'], detected['wheel_bk_r']} - {None}
    if len(assigned_wheels) < 4:
        potential_wheels = wheel_candidates if len(wheel_candidates) >= 4 else remaining
        # Filter out objects already assigned as body
        potential_wheels = [o for o in potential_wheels if o != detected['body']]

        if len(potential_wheels) >= 4:
            # Sort 4 objects by bounds center
            sorted_by_y = sorted(potential_wheels[:4], key=lambda o: (get_object_world_center(o).y if get_object_world_center(o) else 0))
            # 2 front wheels have smaller Y (-Y)
            front_two = sorted_by_y[:2]
            # 2 back wheels have larger Y (+Y)
            back_two = sorted_by_y[2:]

            # In Front: +X is Left, -X is Right
            front_sorted_x = sorted(front_two, key=lambda o: (get_object_world_center(o).x if get_object_world_center(o) else 0), reverse=True)
            # In Back: +X is Left, -X is Right
            back_sorted_x = sorted(back_two, key=lambda o: (get_object_world_center(o).x if get_object_world_center(o) else 0), reverse=True)

            if detected['wheel_ft_l'] is None:
                detected['wheel_ft_l'] = front_sorted_x[0]
            if detected['wheel_ft_r'] is None:
                detected['wheel_ft_r'] = front_sorted_x[1]
            if detected['wheel_bk_l'] is None:
                detected['wheel_bk_l'] = back_sorted_x[0]
            if detected['wheel_bk_r'] is None:
                detected['wheel_bk_r'] = back_sorted_x[1]

    # 4. Detect Brakes
    brake_pattern = re.compile(r'(brake|caliper|rotor|disc)', re.IGNORECASE)
    brake_candidates = [o for o in remaining if brake_pattern.search(o.name)]
    for o in brake_candidates:
        n = o.name
        if detected['brake_ft_l'] is None and fl_pattern.search(n):
            detected['brake_ft_l'] = o
        elif detected['brake_ft_r'] is None and fr_pattern.search(n):
            detected['brake_ft_r'] = o
        elif detected['brake_bk_l'] is None and bl_pattern.search(n):
            detected['brake_bk_l'] = o
        elif detected['brake_bk_r'] is None and br_pattern.search(n):
            detected['brake_bk_r'] = o

    return detected


# ---------------------------------------------------------------------------
# Property Group for Scene UI
# ---------------------------------------------------------------------------

class RigacarCarPartsSettings(bpy.types.PropertyGroup):
    body: bpy.props.PointerProperty(
        name="Body / Chassis",
        type=bpy.types.Object,
        description="Main vehicle body or chassis mesh object"
    )
    wheel_ft_l: bpy.props.PointerProperty(
        name="Front Left Wheel",
        type=bpy.types.Object,
        description="Front-Left wheel mesh object"
    )
    wheel_ft_r: bpy.props.PointerProperty(
        name="Front Right Wheel",
        type=bpy.types.Object,
        description="Front-Right wheel mesh object"
    )
    wheel_bk_l: bpy.props.PointerProperty(
        name="Back Left Wheel",
        type=bpy.types.Object,
        description="Back-Left (rear) wheel mesh object"
    )
    wheel_bk_r: bpy.props.PointerProperty(
        name="Back Right Wheel",
        type=bpy.types.Object,
        description="Back-Right (rear) wheel mesh object"
    )

    # Brakes
    show_brakes: bpy.props.BoolProperty(
        name="Include Brakes / Calipers",
        description="Specify separate brake caliper / rotor objects",
        default=False
    )
    brake_ft_l: bpy.props.PointerProperty(
        name="Front Left Brake",
        type=bpy.types.Object,
        description="Front-Left brake caliper mesh object"
    )
    brake_ft_r: bpy.props.PointerProperty(
        name="Front Right Brake",
        type=bpy.types.Object,
        description="Front-Right brake caliper mesh object"
    )
    brake_bk_l: bpy.props.PointerProperty(
        name="Back Left Brake",
        type=bpy.types.Object,
        description="Back-Left brake caliper mesh object"
    )
    brake_bk_r: bpy.props.PointerProperty(
        name="Back Right Brake",
        type=bpy.types.Object,
        description="Back-Right brake caliper mesh object"
    )

    # Multi-Axle
    show_multi_axle: bpy.props.BoolProperty(
        name="Multi-Axle / Trucks",
        description="Configure extra wheel axle pairs (e.g. 6x6, 8x8)",
        default=False
    )
    nb_front_pairs: bpy.props.IntProperty(
        name="Front Pairs",
        description="Number of front wheel pairs",
        default=1,
        min=1,
        max=5
    )
    nb_back_pairs: bpy.props.IntProperty(
        name="Back Pairs",
        description="Number of back wheel pairs",
        default=1,
        min=1,
        max=5
    )


# ---------------------------------------------------------------------------
# Rig Creation & Alignment Logic
# ---------------------------------------------------------------------------

def build_rig_from_parts(context, generate_anim=False):
    """Create deformation rig sized and aligned precisely to the chosen parts, then parent parts."""
    settings = context.scene.rigacar_car_parts

    # Calculate Body Position & Dimensions
    body_center = get_object_world_center(settings.body) or mathutils.Vector((0.0, 0.0, 0.8))
    body_bounds = get_object_world_bounds(settings.body)
    if body_bounds:
        body_length = max(body_bounds[3] - body_bounds[2], 1.0)
    else:
        body_length = 2.0

    # Calculate Wheel Positions & Radii
    # Default fallbacks if wheels not selected
    wheel_positions = {
        'Wheel.Ft.L': get_object_world_center(settings.wheel_ft_l) or mathutils.Vector((0.9, -1.8, 0.4)),
        'Wheel.Ft.R': get_object_world_center(settings.wheel_ft_r) or mathutils.Vector((-0.9, -1.8, 0.4)),
        'Wheel.Bk.L': get_object_world_center(settings.wheel_bk_l) or mathutils.Vector((0.9, 1.8, 0.4)),
        'Wheel.Bk.R': get_object_world_center(settings.wheel_bk_r) or mathutils.Vector((-0.9, 1.8, 0.4)),
    }

    wheel_radii = {
        'Wheel.Ft.L': get_wheel_radius(settings.wheel_ft_l),
        'Wheel.Ft.R': get_wheel_radius(settings.wheel_ft_r),
        'Wheel.Bk.L': get_wheel_radius(settings.wheel_bk_l),
        'Wheel.Bk.R': get_wheel_radius(settings.wheel_bk_r),
    }

    # Brakes
    has_brakes = settings.show_brakes
    brake_positions = {}
    if has_brakes:
        brake_positions = {
            'WheelBrake.Ft.L': get_object_world_center(settings.brake_ft_l) or (wheel_positions['Wheel.Ft.L'] + mathutils.Vector((-0.1, 0, 0))),
            'WheelBrake.Ft.R': get_object_world_center(settings.brake_ft_r) or (wheel_positions['Wheel.Ft.R'] + mathutils.Vector((0.1, 0, 0))),
            'WheelBrake.Bk.L': get_object_world_center(settings.brake_bk_l) or (wheel_positions['Wheel.Bk.L'] + mathutils.Vector((-0.1, 0, 0))),
            'WheelBrake.Bk.R': get_object_world_center(settings.brake_bk_r) or (wheel_positions['Wheel.Bk.R'] + mathutils.Vector((0.1, 0, 0))),
        }

    # Create new Armature data and Object
    amt = bpy.data.armatures.new('Car Rig Data')
    amt['Car Rig'] = False
    rig = bpy_extras.object_utils.object_data_add(context, amt, name='Car Rig')

    # Switch to EDIT mode to create deformation bones
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = rig.data.edit_bones

    # 1. DEF-Body
    b_body = edit_bones.new('DEF-Body')
    b_body.head = body_center.copy()
    b_body.tail = body_center.copy()
    b_body.tail.y += body_length / 2.0

    # 2. DEF-Wheel bones
    for w_name, w_pos in wheel_positions.items():
        b_w = edit_bones.new('DEF-' + w_name)
        b_w.head = w_pos.copy()
        b_w.tail = w_pos.copy()
        radius = wheel_radii.get(w_name, 0.4)
        b_w.tail.y += radius

    # 3. DEF-WheelBrake bones
    if has_brakes:
        for b_name, b_pos in brake_positions.items():
            b_brk = edit_bones.new('DEF-' + b_name)
            b_brk.head = b_pos.copy()
            b_brk.tail = b_pos.copy()
            b_brk.tail.y += 0.2

    # Deselect all edit bones and switch to OBJECT mode
    for b in edit_bones:
        b.select = False
    bpy.ops.object.mode_set(mode='OBJECT')

    # 4. Parent Chosen Objects to Bones
    if settings.body:
        parent_object_to_bone(settings.body, rig, 'DEF-Body')
    if settings.wheel_ft_l:
        parent_object_to_bone(settings.wheel_ft_l, rig, 'DEF-Wheel.Ft.L')
    if settings.wheel_ft_r:
        parent_object_to_bone(settings.wheel_ft_r, rig, 'DEF-Wheel.Ft.R')
    if settings.wheel_bk_l:
        parent_object_to_bone(settings.wheel_bk_l, rig, 'DEF-Wheel.Bk.L')
    if settings.wheel_bk_r:
        parent_object_to_bone(settings.wheel_bk_r, rig, 'DEF-Wheel.Bk.R')

    if has_brakes:
        if settings.brake_ft_l:
            parent_object_to_bone(settings.brake_ft_l, rig, 'DEF-WheelBrake.Ft.L')
        if settings.brake_ft_r:
            parent_object_to_bone(settings.brake_ft_r, rig, 'DEF-WheelBrake.Ft.R')
        if settings.brake_bk_l:
            parent_object_to_bone(settings.brake_bk_l, rig, 'DEF-WheelBrake.Bk.L')
        if settings.brake_bk_r:
            parent_object_to_bone(settings.brake_bk_r, rig, 'DEF-WheelBrake.Bk.R')

    # Activate Rig
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)

    # 5. Optionally generate animation rig immediately
    if generate_anim:
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.car_animation_rig_generate()

    return rig


def attach_parts_to_existing_rig(context, rig):
    """Parent chosen parts to an existing car rig without modifying bone positions."""
    settings = context.scene.rigacar_car_parts
    attached = 0

    if settings.body and parent_object_to_bone(settings.body, rig, 'DEF-Body'):
        attached += 1
    if settings.wheel_ft_l and parent_object_to_bone(settings.wheel_ft_l, rig, 'DEF-Wheel.Ft.L'):
        attached += 1
    if settings.wheel_ft_r and parent_object_to_bone(settings.wheel_ft_r, rig, 'DEF-Wheel.Ft.R'):
        attached += 1
    if settings.wheel_bk_l and parent_object_to_bone(settings.wheel_bk_l, rig, 'DEF-Wheel.Bk.L'):
        attached += 1
    if settings.wheel_bk_r and parent_object_to_bone(settings.wheel_bk_r, rig, 'DEF-Wheel.Bk.R'):
        attached += 1

    if settings.show_brakes:
        if settings.brake_ft_l and parent_object_to_bone(settings.brake_ft_l, rig, 'DEF-WheelBrake.Ft.L'):
            attached += 1
        if settings.brake_ft_r and parent_object_to_bone(settings.brake_ft_r, rig, 'DEF-WheelBrake.Ft.R'):
            attached += 1
        if settings.brake_bk_l and parent_object_to_bone(settings.brake_bk_l, rig, 'DEF-WheelBrake.Bk.L'):
            attached += 1
        if settings.brake_bk_r and parent_object_to_bone(settings.brake_bk_r, rig, 'DEF-WheelBrake.Bk.R'):
            attached += 1

    return attached


def snap_rig_bones_to_parts(context, rig):
    """Align deformation bones of an existing deformation rig to the chosen parts."""
    if not rig or rig.type != 'ARMATURE':
        return 0
    if rig.data.get('Car Rig', False):
        return -1  # Already generated animation rig

    settings = context.scene.rigacar_car_parts
    prev_mode = rig.mode
    bpy.ops.object.mode_set(mode='EDIT')
    ebs = rig.data.edit_bones

    aligned = 0

    if settings.body and 'DEF-Body' in ebs:
        c = get_object_world_center(settings.body)
        b = get_object_world_bounds(settings.body)
        length = (b[3] - b[2]) if b else 2.0
        ebs['DEF-Body'].head = c
        ebs['DEF-Body'].tail = c + mathutils.Vector((0, length / 2.0, 0))
        aligned += 1

    wheels_map = {
        'DEF-Wheel.Ft.L': settings.wheel_ft_l,
        'DEF-Wheel.Ft.R': settings.wheel_ft_r,
        'DEF-Wheel.Bk.L': settings.wheel_bk_l,
        'DEF-Wheel.Bk.R': settings.wheel_bk_r,
    }

    for b_name, obj in wheels_map.items():
        if obj and b_name in ebs:
            c = get_object_world_center(obj)
            r = get_wheel_radius(obj)
            ebs[b_name].head = c
            ebs[b_name].tail = c + mathutils.Vector((0, r, 0))
            aligned += 1

    bpy.ops.object.mode_set(mode=prev_mode)
    return aligned


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------

class RIGACAR_OT_autoDetectParts(bpy.types.Operator):
    bl_idname = "rigacar.auto_detect_parts"
    bl_label = "Auto-Detect Car Parts"
    bl_description = "Automatically detects Body, Wheels, and Brakes from selected objects or scene meshes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        detected = detect_car_parts(context)
        settings = context.scene.rigacar_car_parts

        count = 0
        if detected['body']:
            settings.body = detected['body']
            count += 1
        if detected['wheel_ft_l']:
            settings.wheel_ft_l = detected['wheel_ft_l']
            count += 1
        if detected['wheel_ft_r']:
            settings.wheel_ft_r = detected['wheel_ft_r']
            count += 1
        if detected['wheel_bk_l']:
            settings.wheel_bk_l = detected['wheel_bk_l']
            count += 1
        if detected['wheel_bk_r']:
            settings.wheel_bk_r = detected['wheel_bk_r']
            count += 1

        brakes_found = False
        for k in ('brake_ft_l', 'brake_ft_r', 'brake_bk_l', 'brake_bk_r'):
            if detected[k]:
                setattr(settings, k, detected[k])
                brakes_found = True
                count += 1

        if brakes_found:
            settings.show_brakes = True

        if count > 0:
            self.report({'INFO'}, f"Auto-detected {count} car parts!")
        else:
            self.report({'WARNING'}, "No matching car parts found. Please select objects or pick them manually.")
        return {'FINISHED'}


class RIGACAR_OT_createRigFromParts(bpy.types.Operator):
    bl_idname = "rigacar.create_rig_from_parts"
    bl_label = "Create Rig from Chosen Parts"
    bl_description = "Creates a car deformation rig perfectly sized and positioned for the chosen car parts"
    bl_options = {'REGISTER', 'UNDO'}

    generate_animation_rig: bpy.props.BoolProperty(
        name="Generate Animation Rig Immediately",
        description="Generate animation rig controls immediately after creating the deformation rig",
        default=False
    )

    def execute(self, context):
        rig = build_rig_from_parts(context, generate_anim=self.generate_animation_rig)
        if self.generate_animation_rig:
            self.report({'INFO'}, "Car animation rig created and generated successfully!")
        else:
            self.report({'INFO'}, "Car deformation rig created from chosen parts! Click 'Generate' when ready.")
        return {'FINISHED'}


class RIGACAR_OT_attachPartsToRig(bpy.types.Operator):
    bl_idname = "rigacar.attach_parts_to_rig"
    bl_label = "Attach Parts to Active Rig"
    bl_description = "Parents the chosen car parts to the corresponding deformation bones of the active rig"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob is not None and ob.type == 'ARMATURE' and 'Car Rig' in ob.data

    def execute(self, context):
        attached = attach_parts_to_existing_rig(context, context.object)
        self.report({'INFO'}, f"Attached {attached} objects to rig!")
        return {'FINISHED'}


class RIGACAR_OT_snapRigToParts(bpy.types.Operator):
    bl_idname = "rigacar.snap_rig_to_parts"
    bl_label = "Snap Bones to Chosen Parts"
    bl_description = "Aligns existing deformation bones to the positions and sizes of the chosen car parts"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob is not None and ob.type == 'ARMATURE' and 'Car Rig' in ob.data and not ob.data.get('Car Rig', False)

    def execute(self, context):
        res = snap_rig_bones_to_parts(context, context.object)
        if res == -1:
            self.report({'WARNING'}, "Animation rig is already generated! Snapping is only available before generation.")
        else:
            self.report({'INFO'}, f"Aligned {res} bones to chosen car parts!")
        return {'FINISHED'}


class RIGACAR_OT_clearParts(bpy.types.Operator):
    bl_idname = "rigacar.clear_parts"
    bl_label = "Clear Chosen Parts"
    bl_description = "Clears all currently selected car part assignments"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.rigacar_car_parts
        settings.body = None
        settings.wheel_ft_l = None
        settings.wheel_ft_r = None
        settings.wheel_bk_l = None
        settings.wheel_bk_r = None
        settings.brake_ft_l = None
        settings.brake_ft_r = None
        settings.brake_bk_l = None
        settings.brake_bk_r = None
        self.report({'INFO'}, "Cleared car parts selection.")
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# UI Panel: Car Parts Setup in 3D View Sidebar
# ---------------------------------------------------------------------------

class RIGACAR_PT_carPartsSetupView(bpy.types.Panel):
    bl_category = "Rigacar"
    bl_label = "Car Parts Setup"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_order = 0

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        settings = context.scene.rigacar_car_parts
        active_obj = context.object
        is_car_rig = active_obj is not None and active_obj.type == 'ARMATURE' and 'Car Rig' in active_obj.data
        is_generated = is_car_rig and active_obj.data.get('Car Rig', False)

        # Quick Actions Row: Auto-Detect & Clear
        row = layout.row(align=True)
        row.operator(RIGACAR_OT_autoDetectParts.bl_idname, text="Auto-Detect Parts", icon='VIEWZOOM')
        row.operator(RIGACAR_OT_clearParts.bl_idname, text="Clear", icon='X')

        layout.separator()

        # 1. Body Section
        col = layout.column(align=True)
        col.prop(settings, "body", text="Body / Chassis", icon='OBJECT_DATA')

        layout.separator()

        # 2. Wheels Section
        box = layout.box()
        box.label(text="Wheels", icon='ORIENTATION_GIMBAL')

        col = box.column(align=True)
        col.prop(settings, "wheel_ft_l", text="Front Left")
        col.prop(settings, "wheel_ft_r", text="Front Right")
        col.separator()
        col.prop(settings, "wheel_bk_l", text="Back Left")
        col.prop(settings, "wheel_bk_r", text="Back Right")

        # 3. Optional Brakes Section
        layout.prop(settings, "show_brakes", text="Include Brakes / Calipers", icon='RESTRICT_SELECT_OFF' if settings.show_brakes else 'RESTRICT_SELECT_ON')
        if settings.show_brakes:
            b_box = layout.box()
            b_col = b_box.column(align=True)
            b_col.prop(settings, "brake_ft_l", text="Front Left Brake")
            b_col.prop(settings, "brake_ft_r", text="Front Right Brake")
            b_col.prop(settings, "brake_bk_l", text="Back Left Brake")
            b_col.prop(settings, "brake_bk_r", text="Back Right Brake")

        layout.separator()

        # 4. Action Buttons depending on current context
        if not is_car_rig:
            # No car rig active yet: give buttons to create
            col = layout.column(align=True)
            col.scale_y = 1.3
            op = col.operator(RIGACAR_OT_createRigFromParts.bl_idname, text="Create Deformation Rig", icon='ARMATURE_DATA')
            op.generate_animation_rig = False

            op2 = col.operator(RIGACAR_OT_createRigFromParts.bl_idname, text="Create & Generate Animation Rig", icon='AUTO')
            op2.generate_animation_rig = True
        elif not is_generated:
            # Deformation rig active, but animation rig not yet generated
            box = layout.box()
            box.label(text="Deformation Rig Active", icon='CHECKMARK')
            col = box.column(align=True)
            col.scale_y = 1.2
            col.operator(RIGACAR_OT_snapRigToParts.bl_idname, text="Snap Bones to Chosen Parts", icon='SNAP_ON')
            col.operator(RIGACAR_OT_attachPartsToRig.bl_idname, text="Attach Parts to Rig", icon='LINKED')

            layout.separator()
            col2 = layout.column(align=True)
            col2.scale_y = 1.4
            col2.operator("pose.car_animation_rig_generate", text="Generate Animation Rig", icon='AUTO')
        else:
            # Animation rig is fully generated
            box = layout.box()
            box.label(text="Animation Rig Active", icon='CHECKMARK')
            col = box.column(align=True)
            col.operator(RIGACAR_OT_attachPartsToRig.bl_idname, text="Re-attach Parts to Rig", icon='LINKED')


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

classes = (
    RigacarCarPartsSettings,
    RIGACAR_OT_autoDetectParts,
    RIGACAR_OT_createRigFromParts,
    RIGACAR_OT_attachPartsToRig,
    RIGACAR_OT_snapRigToParts,
    RIGACAR_OT_clearParts,
    RIGACAR_PT_carPartsSetupView,
)


def register():
    for c in classes:
        try:
            bpy.utils.register_class(c)
        except ValueError:
            pass

    try:
        bpy.types.Scene.rigacar_car_parts = bpy.props.PointerProperty(type=RigacarCarPartsSettings)
    except Exception:
        pass


def unregister():
    if hasattr(bpy.types.Scene, 'rigacar_car_parts'):
        del bpy.types.Scene.rigacar_car_parts

    for c in reversed(classes):
        try:
            bpy.utils.unregister_class(c)
        except RuntimeError:
            pass
