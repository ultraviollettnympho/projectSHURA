"""
SHURA_02 Animation Script for Blender
======================================
Imports the rigged GLB, creates 4 animations from the pipeline:
1. Smooth walking cycle
2. Jumping
3. Cute standing bashful pose (twirling fingers)
4. Striking peace-sign pose + aura glow

Run from Blender's Python console or via command line:
    /Applications/Blender.app/Contents/MacOS/Blender --background --python shura_02_animations.py
"""

import bpy
import math
import os

GLB_PATH = '/Users/ultraviollett/projectSHURA/data/avatars/shura/embeddings/shura-02/04_Rig/shura_02_rigged.glb'
EXPORT_PATH = '/Users/ultraviollett/projectSHURA/data/avatars/shura/embeddings/shura-02/06_Final/web/shura_02_v1_prototype.glb'

def setup_scene():
    """Clear scene and import GLB"""
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Import GLB
    if os.path.exists(GLB_PATH):
        bpy.ops.import_scene.gltf(filepath=GLB_PATH)
        print("Imported GLB:", GLB_PATH)
    else:
        print("ERROR: GLB not found:", GLB_PATH)
        return False
    
    # Report imported objects
    print("Imported objects:")
    for obj in bpy.context.scene.objects:
        print(f"  {obj.name} ({obj.type})")
        if obj.type == 'ARMATURE':
            print(f"    Bones: {len(obj.pose.bones)}")
            for bone in obj.pose.bones:
                print(f"      {bone.name}")
    
    return True

def clear_all_actions():
    """Remove all existing actions"""
    for action in bpy.data.actions:
        bpy.data.actions.remove(action)

def find_armature():
    """Find the armature object"""
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE':
            return obj
    return None

def find_bone(armature, name):
    """Find a bone by name with fallback"""
    bone = armature.pose.bones.get(name)
    if bone:
        return bone
    # Try case-insensitive
    for b in armature.pose.bones:
        if b.name.lower() == name.lower():
            return b
    return None

def keyframe_bone(armature, bone_name, frame, location=None, rotation_euler=None, scale=None):
    """Add a keyframe to a bone"""
    bone = find_bone(armature, bone_name)
    if not bone:
        return False
    
    if location is not None:
        bone.location = location
        bone.keyframe_insert(data_path="location", frame=frame)
    if rotation_euler is not None:
        bone.rotation_euler = rotation_euler
        bone.keyframe_insert(data_path="rotation_euler", frame=frame)
    if scale is not None:
        bone.scale = scale
        bone.keyframe_insert(data_path="scale", frame=frame)
    return True

def create_walk_cycle():
    """Smooth walking cycle with root motion, hip sway, arm swing, leg movement."""
    action = bpy.data.actions.new(name="walk-cycle")
    armature = find_armature()
    if not armature:
        return
    
    # Find bones with fallbacks
    hips = find_bone(armature, 'Hips')
    spine = find_bone(armature, 'Spine')
    head = find_bone(armature, 'Head')
    left_arm = find_bone(armature, 'LUpperArm') or find_bone(armature, 'LShoulder')
    right_arm = find_bone(armature, 'RUpperArm') or find_bone(armature, 'RShoulder')
    left_leg = find_bone(armature, 'LThigh')
    right_leg = find_bone(armature, 'RThigh')
    
    frames = [0, 6, 12, 18, 24, 30, 36]
    
    for frame in frames:
        t = frame / 36.0
        
        if hips:
            # Root motion forward + slight bounce
            hips.location = (0, frame * 0.1, abs(math.sin(t * math.pi * 2)) * 0.05)
            hips.keyframe_insert(data_path="location", frame=frame)
        
        if spine:
            # Hip sway
            spine.rotation_euler = (0, math.sin(t * math.pi * 2) * 0.1, 0)
            spine.keyframe_insert(data_path="rotation_euler", frame=frame)
        
        if left_arm:
            left_arm.rotation_euler = (math.sin(t * math.pi * 2) * 0.3, 0, 0)
            left_arm.keyframe_insert(data_path="rotation_euler", frame=frame)
        
        if right_arm:
            right_arm.rotation_euler = (-math.sin(t * math.pi * 2) * 0.3, 0, 0)
            right_arm.keyframe_insert(data_path="rotation_euler", frame=frame)
        
        if left_leg:
            left_leg.rotation_euler = (math.sin(t * math.pi * 2) * 0.4, 0, 0)
            left_leg.keyframe_insert(data_path="rotation_euler", frame=frame)
        
        if right_leg:
            right_leg.rotation_euler = (-math.sin(t * math.pi * 2) * 0.4, 0, 0)
            right_leg.keyframe_insert(data_path="rotation_euler", frame=frame)
        
        if head:
            head.rotation_euler = (math.sin(t * math.pi * 4) * 0.05, 0, 0)
            head.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    armature.animation_data_create()
    armature.animation_data.action = action
    action.use_cyclic = True
    print("Created walk-cycle animation")

def create_jump():
    """Anticipation → launch → apex → landing."""
    action = bpy.data.actions.new(name="jump")
    armature = find_armature()
    if not armature:
        return
    
    hips = find_bone(armature, 'Hips')
    left_arm = find_bone(armature, 'LUpperArm') or find_bone(armature, 'LShoulder')
    right_arm = find_bone(armature, 'RUpperArm') or find_bone(armature, 'RShoulder')
    left_leg = find_bone(armature, 'LThigh')
    right_leg = find_bone(armature, 'RThigh')
    
    # Anticipation (crouch)
    keyframe_bone(armature, 'Hips', 0, location=(0, 0, 0))
    keyframe_bone(armature, 'Hips', 8, location=(0, 0, -0.3))
    
    # Launch
    keyframe_bone(armature, 'Hips', 14, location=(0, 0, 0.5))
    
    # Apex
    keyframe_bone(armature, 'Hips', 18, location=(0, 0, 1.2))
    
    # Landing
    keyframe_bone(armature, 'Hips', 24, location=(0, 0, 0.5))
    keyframe_bone(armature, 'Hips', 30, location=(0, 0, -0.2))
    keyframe_bone(armature, 'Hips', 36, location=(0, 0, 0))
    
    # Arms swing
    for frame, rot in [(0, (0,0,0)), (8, (-0.5,0,0)), (18, (-1.5,0,0)), (36, (0,0,0))]:
        keyframe_bone(armature, 'LUpperArm', frame, rotation_euler=rot)
        keyframe_bone(armature, 'RUpperArm', frame, rotation_euler=rot)
    
    # Legs tuck
    for frame, rot in [(0, (0,0,0)), (8, (0.8,0,0)), (18, (0.3,0,0)), (36, (0,0,0))]:
        keyframe_bone(armature, 'LThigh', frame, rotation_euler=rot)
        keyframe_bone(armature, 'RThigh', frame, rotation_euler=rot)
    
    armature.animation_data_create()
    armature.animation_data.action = action
    print("Created jump animation")

def create_bashful_pose():
    """Cute bashful pose: hip tilt, head down, hand near face."""
    action = bpy.data.actions.new(name="bashful-pose")
    armature = find_armature()
    if not armature:
        return
    
    spine = find_bone(armature, 'Spine')
    head = find_bone(armature, 'Head')
    right_arm = find_bone(armature, 'RUpperArm') or find_bone(armature, 'RShoulder')
    left_arm = find_bone(armature, 'LUpperArm') or find_bone(armature, 'LShoulder')
    hips = find_bone(armature, 'Hips')
    
    for frame, sway in [(0, 0.15), (24, 0.2), (48, 0.15)]:
        if spine:
            spine.rotation_euler = (0, 0, sway)
            spine.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    for frame, tilt in [(0, (0.1, 0.2, 0.1)), (24, (0.15, 0.25, 0.15)), (48, (0.1, 0.2, 0.1))]:
        if head:
            head.rotation_euler = tilt
            head.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    for frame, rot in [(0, (-0.8, 0.3, 0.2)), (24, (-0.9, 0.4, 0.3)), (48, (-0.8, 0.3, 0.2))]:
        if right_arm:
            right_arm.rotation_euler = rot
            right_arm.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if left_arm:
        left_arm.rotation_euler = (0, 0, -0.1)
        left_arm.keyframe_insert(data_path="rotation_euler", frame=0)
    
    for frame, sway in [(0, (0,0,0.05)), (24, (0,0,-0.05)), (48, (0,0,0.05))]:
        if hips:
            hips.rotation_euler = sway
            hips.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    armature.animation_data_create()
    armature.animation_data.action = action
    action.use_cyclic = True
    print("Created bashful-pose animation")

def create_peace_sign_pose():
    """Peace sign pose: confident stance, hand raised with peace sign, aura glow."""
    action = bpy.data.actions.new(name="peace-sign-pose")
    armature = find_armature()
    if not armature:
        return
    
    spine = find_bone(armature, 'Spine')
    head = find_bone(armature, 'Head')
    right_arm = find_bone(armature, 'RUpperArm') or find_bone(armature, 'RShoulder')
    left_arm = find_bone(armature, 'LUpperArm') or find_bone(armature, 'LShoulder')
    hips = find_bone(armature, 'Hips')
    
    if spine:
        spine.rotation_euler = (0, 0, 0.1)
        spine.keyframe_insert(data_path="rotation_euler", frame=0)
    
    for frame, rot in [(0, (-0.05, 0, 0)), (24, (-0.1, 0, 0)), (48, (-0.05, 0, 0))]:
        if head:
            head.rotation_euler = rot
            head.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    for frame, rot in [(0, (-2.5, 0.5, 0.3)), (24, (-2.6, 0.6, 0.4)), (48, (-2.5, 0.5, 0.3))]:
        if right_arm:
            right_arm.rotation_euler = rot
            right_arm.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if left_arm:
        left_arm.rotation_euler = (0, 0, -0.15)
        left_arm.keyframe_insert(data_path="rotation_euler", frame=0)
    
    for frame, rot in [(0, (0,0,0.05)), (24, (0,0,-0.05)), (48, (0,0,0.05))]:
        if hips:
            hips.rotation_euler = rot
            hips.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    armature.animation_data_create()
    armature.animation_data.action = action
    action.use_cyclic = True
    print("Created peace-sign-pose animation")

def setup_aura():
    """Add pink/purple emission aura material"""
    for mat in bpy.data.materials:
        if mat.use_nodes:
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            
            emission = nodes.new('ShaderNodeEmission')
            emission.inputs['Color'].default_value = (1.0, 0.16, 0.54, 1.0)
            emission.inputs['Strength'].default_value = 2.0
            
            mix = nodes.new('ShaderNodeMixShader')
            output = nodes.get('Material Output')
            bsdf = nodes.get('Principled BSDF')
            
            if output and bsdf:
                links.new(mix.outputs[0], output.inputs['Surface'])
                links.new(bsdf.outputs[0], mix.inputs[1])
                links.new(emission.outputs[0], mix.inputs[2])
    
    print("Aura material setup complete")

def export_animations():
    """Export all animations as GLB"""
    bpy.ops.export_scene.gltf(
        filepath=EXPORT_PATH,
        export_format='GLB',
        export_animations=True,
        export_animation_mode='ACTIONS',
        export_skins=True,
        export_morph=True,
        export_apply=True,
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_draco_position_quantization=14,
        export_draco_normal_quantization=10,
        export_draco_texcoord_quantization=12,
        export_draco_color_quantization=10,
        export_draco_generic_quantization=12,
    )
    print("Exported:", EXPORT_PATH)

# Main
if __name__ == '__main__':
    print("=== SHURA_02 Animation Pipeline ===")
    
    if not setup_scene():
        print("Failed to setup scene")
    else:
        create_walk_cycle()
        create_jump()
        create_bashful_pose()
        create_peace_sign_pose()
        setup_aura()
        export_animations()
        print("=== Pipeline Complete ===")
