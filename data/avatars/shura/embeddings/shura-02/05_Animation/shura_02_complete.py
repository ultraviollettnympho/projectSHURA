"""
SHURA_02 Complete Animation Pipeline
=====================================
Imports rigged GLB, creates 4 animations, pushes to NLA, exports.

Run: /Applications/Blender.app/Contents/MacOS/Blender --background --python shura_02_complete.py
"""

import bpy
import math
import os

GLB_PATH = '/Users/ultraviollett/projectSHURA/data/avatars/shura/embeddings/shura-02/04_Rig/shura_02_rigged.glb'
EXPORT_PATH = '/Users/ultraviollett/projectSHURA/data/avatars/shura/embeddings/shura-02/06_Final/web/shura_02_v1_prototype.glb'

def clear_scene():
    """Remove all objects"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def import_glb():
    """Import the rigged GLB file"""
    if not os.path.exists(GLB_PATH):
        print("ERROR: GLB not found:", GLB_PATH)
        return False
    
    bpy.ops.import_scene.gltf(filepath=GLB_PATH)
    print("Imported:", GLB_PATH)
    
    # Report
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE':
            print(f"Armature: {obj.name} with {len(obj.pose.bones)} bones")
        elif obj.type == 'MESH':
            print(f"Mesh: {obj.name}")
    
    return True

def get_armature():
    """Get the armature object"""
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE':
            return obj
    return None

def find_bone(armature, *names):
    """Find a bone by trying multiple name variants"""
    for name in names:
        bone = armature.pose.bones.get(name)
        if bone:
            return bone
    # Try case-insensitive
    for b in armature.pose.bones:
        for name in names:
            if b.name.lower() == name.lower():
                return b
    return None

def set_keyframe(bone, frame, location=None, rotation=None):
    """Set keyframe on bone"""
    if location is not None:
        bone.location = location
        bone.keyframe_insert(data_path="location", frame=frame)
    if rotation is not None:
        bone.rotation_euler = rotation
        bone.keyframe_insert(data_path="rotation_euler", frame=frame)

def create_walk_cycle(armature):
    """1. Smooth walking cycle with root motion, hip sway, arm swing."""
    action = bpy.data.actions.new(name="walk-cycle")
    
    bones = armature.pose.bones
    hips = find_bone(armature, 'Hips')
    spine = find_bone(armature, 'Spine')
    head = find_bone(armature, 'Head')
    l_arm = find_bone(armature, 'LUpperArm', 'LShoulder')
    r_arm = find_bone(armature, 'RUpperArm', 'RShoulder')
    l_leg = find_bone(armature, 'LThigh')
    r_leg = find_bone(armature, 'RThigh')
    
    for frame in [0, 6, 12, 18, 24, 30, 36]:
        t = frame / 36.0
        
        if hips:
            set_keyframe(hips, frame, location=(0, frame * 0.1, abs(math.sin(t * math.pi * 2)) * 0.05))
        if spine:
            set_keyframe(spine, frame, rotation=(0, math.sin(t * math.pi * 2) * 0.1, 0))
        if l_arm:
            set_keyframe(l_arm, frame, rotation=(math.sin(t * math.pi * 2) * 0.3, 0, 0))
        if r_arm:
            set_keyframe(r_arm, frame, rotation=(-math.sin(t * math.pi * 2) * 0.3, 0, 0))
        if l_leg:
            set_keyframe(l_leg, frame, rotation=(math.sin(t * math.pi * 2) * 0.4, 0, 0))
        if r_leg:
            set_keyframe(r_leg, frame, rotation=(-math.sin(t * math.pi * 2) * 0.4, 0, 0))
        if head:
            set_keyframe(head, frame, rotation=(math.sin(t * math.pi * 4) * 0.05, 0, 0))
    
    # Assign to armature and make cyclic
    armature.animation_data_create()
    armature.animation_data.action = action
    action.use_cyclic = True
    
    # Push to NLA
    track = armature.animation_data.nla_tracks.new()
    track.strips.new(action.name, 0, action)
    track.name = action.name
    
    print("Created walk-cycle")

def create_jump(armature):
    """2. Anticipation → launch → apex → landing."""
    action = bpy.data.actions.new(name="jump")
    
    hips = find_bone(armature, 'Hips')
    l_arm = find_bone(armature, 'LUpperArm', 'LShoulder')
    r_arm = find_bone(armature, 'RUpperArm', 'RShoulder')
    l_leg = find_bone(armature, 'LThigh')
    r_leg = find_bone(armature, 'RThigh')
    
    # Root motion
    if hips:
        set_keyframe(hips, 0, location=(0, 0, 0))
        set_keyframe(hips, 8, location=(0, 0, -0.3))
        set_keyframe(hips, 14, location=(0, 0, 0.5))
        set_keyframe(hips, 18, location=(0, 0, 1.2))
        set_keyframe(hips, 24, location=(0, 0, 0.5))
        set_keyframe(hips, 30, location=(0, 0, -0.2))
        set_keyframe(hips, 36, location=(0, 0, 0))
    
    # Arms
    for frame, rot in [(0, (0,0,0)), (8, (-0.5,0,0)), (18, (-1.5,0,0)), (36, (0,0,0))]:
        if l_arm: set_keyframe(l_arm, frame, rotation=rot)
        if r_arm: set_keyframe(r_arm, frame, rotation=rot)
    
    # Legs
    for frame, rot in [(0, (0,0,0)), (8, (0.8,0,0)), (18, (0.3,0,0)), (36, (0,0,0))]:
        if l_leg: set_keyframe(l_leg, frame, rotation=rot)
        if r_leg: set_keyframe(r_leg, frame, rotation=rot)
    
    armature.animation_data_create()
    armature.animation_data.action = action
    
    track = armature.animation_data.nla_tracks.new()
    track.strips.new(action.name, 0, action)
    track.name = action.name
    
    print("Created jump")

def create_bashful_pose(armature):
    """3. Cute standing bashful pose."""
    action = bpy.data.actions.new(name="bashful-pose")
    
    spine = find_bone(armature, 'Spine')
    head = find_bone(armature, 'Head')
    r_arm = find_bone(armature, 'RUpperArm', 'RShoulder')
    l_arm = find_bone(armature, 'LUpperArm', 'LShoulder')
    hips = find_bone(armature, 'Hips')
    
    for frame, sway in [(0, 0.15), (24, 0.2), (48, 0.15)]:
        if spine: set_keyframe(spine, frame, rotation=(0, 0, sway))
    
    for frame, tilt in [(0, (0.1, 0.2, 0.1)), (24, (0.15, 0.25, 0.15)), (48, (0.1, 0.2, 0.1))]:
        if head: set_keyframe(head, frame, rotation=tilt)
    
    for frame, rot in [(0, (-0.8, 0.3, 0.2)), (24, (-0.9, 0.4, 0.3)), (48, (-0.8, 0.3, 0.2))]:
        if r_arm: set_keyframe(r_arm, frame, rotation=rot)
    
    if l_arm: set_keyframe(l_arm, 0, rotation=(0, 0, -0.1))
    
    for frame, sway in [(0, (0,0,0.05)), (24, (0,0,-0.05)), (48, (0,0,0.05))]:
        if hips: set_keyframe(hips, frame, rotation=sway)
    
    armature.animation_data_create()
    armature.animation_data.action = action
    action.use_cyclic = True
    
    track = armature.animation_data.nla_tracks.new()
    track.strips.new(action.name, 0, action)
    track.name = action.name
    
    print("Created bashful-pose")

def create_peace_sign_pose(armature):
    """4. Peace sign pose with aura glow."""
    action = bpy.data.actions.new(name="peace-sign-pose")
    
    spine = find_bone(armature, 'Spine')
    head = find_bone(armature, 'Head')
    r_arm = find_bone(armature, 'RUpperArm', 'RShoulder')
    l_arm = find_bone(armature, 'LUpperArm', 'LShoulder')
    hips = find_bone(armature, 'Hips')
    
    if spine: set_keyframe(spine, 0, rotation=(0, 0, 0.1))
    
    for frame, rot in [(0, (-0.05, 0, 0)), (24, (-0.1, 0, 0)), (48, (-0.05, 0, 0))]:
        if head: set_keyframe(head, frame, rotation=rot)
    
    for frame, rot in [(0, (-2.5, 0.5, 0.3)), (24, (-2.6, 0.6, 0.4)), (48, (-2.5, 0.5, 0.3))]:
        if r_arm: set_keyframe(r_arm, frame, rotation=rot)
    
    if l_arm: set_keyframe(l_arm, 0, rotation=(0, 0, -0.15))
    
    for frame, rot in [(0, (0,0,0.05)), (24, (0,0,-0.05)), (48, (0,0,0.05))]:
        if hips: set_keyframe(hips, frame, rotation=rot)
    
    armature.animation_data_create()
    armature.animation_data.action = action
    action.use_cyclic = True
    
    track = armature.animation_data.nla_tracks.new()
    track.strips.new(action.name, 0, action)
    track.name = action.name
    
    print("Created peace-sign-pose")

def add_aura():
    """Add emissive aura to materials"""
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
    
    print("Aura added")

def export_glb():
    """Export with all NLA tracks"""
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
    
    # Count animations
    count = 0
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE' and obj.animation_data:
            count = len(obj.animation_data.nla_tracks)
    print("NLA tracks:", count)

# Main
print("=== SHURA_02 Pipeline ===")
clear_scene()

if import_glb():
    armature = get_armature()
    if armature:
        create_walk_cycle(armature)
        create_jump(armature)
        create_bashful_pose(armature)
        create_peace_sign_pose(armature)
        add_aura()
        export_glb()
        print("=== COMPLETE ===")
    else:
        print("ERROR: No armature found")
else:
    print("ERROR: Import failed")
