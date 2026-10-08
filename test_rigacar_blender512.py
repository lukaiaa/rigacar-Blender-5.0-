import bpy
import sys
import math

print("=== STARTING RIGACAR TEST IN BLENDER 5.1.2 ===")
print("Blender version:", bpy.app.version_string)

# 1. Register addon
sys.path.insert(0, r"d:\_Work\Blender Addons")
import car
car.register()
print("✓ car.register() succeeded")

# 2. Add deformation rig with mesh targets
bpy.ops.wm.read_factory_settings(use_empty=True)
car.register()

# Create dummy body mesh
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
body_obj = bpy.context.active_object
body_obj.name = "DEF-Body"
body_obj.dimensions = (2.0, 4.0, 1.2)

# Create dummy wheel meshes
for name, pos in [
    ("DEF-Wheel.Ft.L", (1.0, -1.5, 0.4)),
    ("DEF-Wheel.Ft.R", (-1.0, -1.5, 0.4)),
    ("DEF-Wheel.Bk.L", (1.0, 1.5, 0.4)),
    ("DEF-Wheel.Bk.R", (-1.0, 1.5, 0.4)),
]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=0.2, location=pos)
    w_obj = bpy.context.active_object
    w_obj.name = name

# Select all
for obj in bpy.data.objects:
    obj.select_set(True)

print("Step 2: Adding deformation rig with auto-detected targets...")
bpy.ops.object.armature_car_deformation_rig()
rig = bpy.context.active_object
assert rig is not None and rig.type == 'ARMATURE', "Rig not created!"
print("✓ Rig created:", rig.name)

# 3. Generate animation rig
print("Step 3: Generating animation rig...")
bpy.ops.object.mode_set(mode='POSE')
bpy.ops.pose.car_animation_rig_generate()
assert rig.data.get('Car Rig') == True, "Car Rig property not set to True!"
print("✓ Animation rig generated!")

# Verify Bone collections
print("Step 4: Verifying bone collections...")
cols = [c.name for c in rig.data.collections]
print("Collections found:", cols)
expected_cols = ['CarRig_Default_Ctrls', 'CarRig_Custom_Ctrls', 'CarRig_Def_Bone', 'CarRig_MCH_Bone', 'CarRig_MCH_Bone_Ext']
for ec in expected_cols:
    assert ec in cols, f"Collection {ec} missing!"
print("✓ All expected bone collections present!")

# 5. Animate Root Bone
print("Step 5: Animating Root bone (path with translation and turning)...")
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 40
root = rig.pose.bones['Root']
root.rotation_mode = 'XYZ'

for frame, loc, rot_z in [
    (1, (0, 0, 0), 0),
    (20, (0, 10, 0), 0.2),
    (40, (5, 20, 0), 0.5),
]:
    bpy.context.scene.frame_set(frame)
    root.location = loc
    root.rotation_euler = (0, 0, rot_z)
    root.keyframe_insert(data_path='location', frame=frame)
    root.keyframe_insert(data_path='rotation_euler', frame=frame)

# 6. Test Wheels Rotation Bake
print("Step 6: Baking wheels rotation...")
bpy.ops.anim.car_wheels_rotation_bake(frame_start=1, frame_end=40)
print("✓ Wheels rotation bake operator executed!")

# Check that rotation keyframes were created
action = rig.animation_data.action
assert action is not None, "Action is None!"
from car.bake_operators import find_fcurve_in_action
fc_wheel = find_fcurve_in_action(action, '["Wheel.rotation.Ft.L"]', index=0, obj=rig)
assert fc_wheel is not None, '["Wheel.rotation.Ft.L"] FCurve not found!'
print(f"✓ Found Wheel.rotation.Ft.L F-Curve with {len(fc_wheel.keyframe_points)} keyframes!")
assert len(fc_wheel.keyframe_points) > 0, "No keyframes in Wheel.rotation.Ft.L!"

# 7. Test Steering Bake
print("Step 7: Baking steering...")
bpy.ops.anim.car_steering_bake(frame_start=1, frame_end=40)
fc_steering = find_fcurve_in_action(action, '["Steering.rotation"]', index=0, obj=rig)
assert fc_steering is not None, '["Steering.rotation"] FCurve not found!'
print(f"✓ Found Steering.rotation F-Curve with {len(fc_steering.keyframe_points)} keyframes!")
assert len(fc_steering.keyframe_points) > 0, "No keyframes in Steering.rotation!"

# 8. Test Clear Baked Animation
print("Step 8: Clearing baked animation...")
bpy.ops.anim.car_clear_steering_wheels_rotation(clear_steering=True, clear_wheels=True)
fc_wheel_cleared = find_fcurve_in_action(action, '["Wheel.rotation.Ft.L"]', index=0, obj=rig)
assert fc_wheel_cleared is None, "Wheel rotation FCurve was not cleared!"
fc_steering_cleared = find_fcurve_in_action(action, '["Steering.rotation"]', index=0, obj=rig)
assert fc_steering_cleared is None, "Steering rotation FCurve was not cleared!"
print("✓ Baked animation cleared successfully!")

# 9. Test adding missing brake bones
print("Step 9: Testing car_animation_add_brake_wheel_bones...")
from car.bake_operators import select_bone
for pb in rig.pose.bones:
    select_bone(rig, pb.name, False)
select_bone(rig, 'Wheel.Ft.L', True)
bpy.ops.pose.car_animation_add_brake_wheel_bones()
print("✓ car_animation_add_brake_wheel_bones executed successfully!")

# 10. Unregister
car.unregister()
print("✓ car.unregister() succeeded")

print("=== ALL RIGACAR TESTS PASSED FOR BLENDER 5.1.2! ===")
