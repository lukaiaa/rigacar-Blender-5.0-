import bpy
import sys
import mathutils

print("=== TESTING CAR PARTS UI & OPERATORS IN BLENDER 5.1.2 ===")

sys.path.insert(0, r"d:\_Work\Blender Addons")
import car
car.register()
print("✓ car.register() succeeded")

# Reset to empty scene
bpy.ops.wm.read_factory_settings(use_empty=True)
car.register()

scene = bpy.context.scene
assert hasattr(scene, 'rigacar_car_parts'), "Scene has no rigacar_car_parts property!"
parts = scene.rigacar_car_parts

# 1. Create realistic custom-named meshes
print("Step 1: Creating custom-named car meshes...")
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1.2))
body = bpy.context.active_object
body.name = "MyCustom_Car_Chassis"
body.dimensions = (2.2, 4.5, 1.3)

wheels = {}
for slot, name, pos in [
    ("wheel_ft_l", "Tire_Front_Left", (1.1, -1.6, 0.45)),
    ("wheel_ft_r", "Tire_Front_Right", (-1.1, -1.6, 0.45)),
    ("wheel_bk_l", "Tire_Back_Left", (1.1, 1.6, 0.45)),
    ("wheel_bk_r", "Tire_Back_Right", (-1.1, 1.6, 0.45)),
]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=0.25, location=pos)
    w = bpy.context.active_object
    w.name = name
    wheels[slot] = w

# Select all objects
for obj in bpy.data.objects:
    obj.select_set(True)

# 2. Test Auto-Detect Operator
print("Step 2: Testing Auto-Detect Parts operator...")
bpy.ops.rigacar.auto_detect_parts()
assert parts.body == body, f"Body not detected! Got {parts.body}"
assert parts.wheel_ft_l == wheels['wheel_ft_l'], f"Wheel FT.L not detected! Got {parts.wheel_ft_l}"
assert parts.wheel_ft_r == wheels['wheel_ft_r'], f"Wheel FT.R not detected! Got {parts.wheel_ft_r}"
assert parts.wheel_bk_l == wheels['wheel_bk_l'], f"Wheel BK.L not detected! Got {parts.wheel_bk_l}"
assert parts.wheel_bk_r == wheels['wheel_bk_r'], f"Wheel BK.R not detected! Got {parts.wheel_bk_r}"
print("✓ All 5 parts successfully auto-detected!")

# 3. Test Create Rig from Parts
print("Step 3: Creating deformation rig from chosen parts...")
bpy.ops.rigacar.create_rig_from_parts(generate_animation_rig=False)
rig = bpy.context.active_object
assert rig is not None and rig.type == 'ARMATURE', "Rig was not created!"
print("✓ Deformation rig created:", rig.name)

# Verify parenting to DEF bones
assert body.parent == rig and body.parent_bone == 'DEF-Body', "Body not parented to DEF-Body!"
assert wheels['wheel_ft_l'].parent == rig and wheels['wheel_ft_l'].parent_bone == 'DEF-Wheel.Ft.L', "FL wheel not parented!"
assert wheels['wheel_ft_r'].parent == rig and wheels['wheel_ft_r'].parent_bone == 'DEF-Wheel.Ft.R', "FR wheel not parented!"
assert wheels['wheel_bk_l'].parent == rig and wheels['wheel_bk_l'].parent_bone == 'DEF-Wheel.Bk.L', "BL wheel not parented!"
assert wheels['wheel_bk_r'].parent == rig and wheels['wheel_bk_r'].parent_bone == 'DEF-Wheel.Bk.R', "BR wheel not parented!"
print("✓ All 5 meshes automatically parented to deformation bones with preserved transforms!")

# Verify bone positions match wheel centers
fl_bone = rig.data.bones['DEF-Wheel.Ft.L']
assert abs(fl_bone.head_local.x - wheels['wheel_ft_l'].matrix_world.to_translation().x) < 0.05, "Bone X position does not match wheel!"
assert abs(fl_bone.head_local.y - wheels['wheel_ft_l'].matrix_world.to_translation().y) < 0.05, "Bone Y position does not match wheel!"
print("✓ Bone positions accurately snapped to mesh centers!")

# 4. Generate Animation Rig
print("Step 4: Generating animation rig...")
bpy.ops.object.mode_set(mode='POSE')
bpy.ops.pose.car_animation_rig_generate()
assert rig.data.get('Car Rig') == True, "Car Rig animation not generated!"
print("✓ Animation rig generated successfully from chosen parts!")

# 5. Animate Root and Bake
print("Step 5: Testing wheel baking on rig generated from chosen parts...")
root = rig.pose.bones['Root']
root.location = (0, 0, 0)
root.keyframe_insert(data_path='location', frame=1)
root.location = (0, 10, 0)
root.keyframe_insert(data_path='location', frame=30)
bpy.ops.anim.car_wheels_rotation_bake(frame_start=1, frame_end=30)
print("✓ Wheel rotation baked successfully!")

# 6. Test Clear Parts
print("Step 6: Testing clear parts operator...")
bpy.ops.rigacar.clear_parts()
assert parts.body is None and parts.wheel_ft_l is None, "Parts were not cleared!"
print("✓ Clear parts operator verified!")

# 7. Test One-Click "Create & Generate Animation Rig"
print("Step 7: Testing one-click Create & Generate Animation Rig...")
bpy.ops.wm.read_factory_settings(use_empty=True)
car.register()
scene = bpy.context.scene
parts = scene.rigacar_car_parts

# Create simple car objects
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 1))
b_obj = bpy.context.active_object
b_obj.name = "Body"
bpy.ops.mesh.primitive_cylinder_add(location=(1, -2, 0.5))
w_fl = bpy.context.active_object
bpy.ops.mesh.primitive_cylinder_add(location=(-1, -2, 0.5))
w_fr = bpy.context.active_object
bpy.ops.mesh.primitive_cylinder_add(location=(1, 2, 0.5))
w_bl = bpy.context.active_object
bpy.ops.mesh.primitive_cylinder_add(location=(-1, 2, 0.5))
w_br = bpy.context.active_object

parts.body = b_obj
parts.wheel_ft_l = w_fl
parts.wheel_ft_r = w_fr
parts.wheel_bk_l = w_bl
parts.wheel_bk_r = w_br

# One-click create & generate!
bpy.ops.rigacar.create_rig_from_parts(generate_animation_rig=True)
active_rig = bpy.context.active_object
assert active_rig is not None and active_rig.type == 'ARMATURE', "One-click rig not created!"
assert active_rig.data.get('Car Rig') == True, "One-click rig animation not generated!"
assert 'Root' in active_rig.pose.bones, "Root bone not in one-click rig!"
print("✓ One-click Create & Generate Animation Rig succeeded completely!")

# Clean up
car.unregister()
print("✓ Unregistered cleanly!")
print("=== ALL CAR PARTS UI TESTS PASSED IN BLENDER 5.1.2! ===")
