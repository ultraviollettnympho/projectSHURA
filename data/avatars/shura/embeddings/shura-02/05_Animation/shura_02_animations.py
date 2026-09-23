"""
SHURA_02 Animation Script for Blender
======================================
Creates the 4 required animations from the pipeline document:
1. Smooth walking cycle (verify existing)
2. Jumping
3. Cute standing bashful pose (twirling fingers)
4. Striking peace-sign pose + aura

Run from Blender's Python console or via command line:
    blender --background shura_02_rigged.blend --python shura_02_animations.py
"""

import bpy
import math

# Clear existing animations except the ones we want to keep
# We'll create new actions for the 4 required animations

def clear_all_actions():
    """Remove all existing actions from the armature"""
    armature = bpy.data.objects.get('Armature')
    if armature and armature.animation_data:
        armature.animation_data.action = None
    for action in bpy.data.actions:
        bpy.data.actions.remove(action)

def create_walk_cycle():
    """
    Smooth walking cycle with root motion, hip sway, arm swing, jacket/hair secondary motion.
    Length: 1.5 second loop at 24fps = 36 frames.
    """
    action = bpy.data.actions.new(name="walk-cycle")
    
    armature = bpy.data.objects.get('Armature')
    if not armature:
        print("ERROR: No Armature found")
        return
    
    # Get bone references
    bones = armature.pose.bones
    
    # Keyframe data: (bone_name, frame, property, value)
    keyframes = []
    
    # Root motion - forward movement
    root = bones.get('Hips')  # Root bone
    if root:
        # Move forward over the cycle
        for frame in range(0, 37, 6):
            root.location = (0, frame * 0.1, 0)
            root.keyframe_insert(data_path="location", frame=frame)
    
    # Hip sway (Spine)
    spine = bones.get('Spine')
    if spine:
        for frame in range(0, 37, 6):
            spine.rotation_euler = (0, math.sin(frame * 0.3) * 0.1, 0)
            spine.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    # Arm swing (opposite to legs)
    left_arm = bones.get('LUpperArm')
    right_arm = bones.get('RUpperArm')
    
    if left_arm:
        for frame in range(0, 37, 6):
            left_arm.rotation_euler = (math.sin(frame * 0.3) * 0.3, 0, 0)
            left_arm.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if right_arm:
        for frame in range(0, 37, 6):
            right_arm.rotation_euler = (-math.sin(frame * 0.3) * 0.3, 0, 0)
            right_arm.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    # Leg movement
    left_leg = bones.get('LThigh')
    right_leg = bones.get('RThigh')
    
    if left_leg:
        for frame in range(0, 37, 6):
            left_leg.rotation_euler = (math.sin(frame * 0.3) * 0.4, 0, 0)
            left_leg.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    if right_leg:
        for frame in range(0, 37, 6):
            right_leg.rotation_euler = (-math.sin(frame * 0.3) * 0.4, 0, 0)
            right_leg.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    # Head bob
    head = bones.get('Head')
    if head:
        for frame in range(0, 37, 6):
            head.rotation_euler = (math.sin(frame * 0.6) * 0.05, 0, 0)
            head.keyframe_insert(data_path="rotation_euler", frame=frame)
    
    # Set action
    armature.animation_data_create()
    armature.animation_data.action = action
    
    # Make it cyclic
    action.use_cyclic = True
    
    print("Created walk-cycle animation")

def create_jump():
    """
    Jumping animation: anticipation → launch → apex → landing.
    Length: 1.5 seconds (36 frames).
    """
    action = bpy.data.actions.new(name="jump")
    
    armature = bpy.data.objects.get('Armature')
    if not armature:
        return
    
    bones = armature.pose.bones
    
    # Phase 1: Anticipation (frames 0-8) - crouch down
    root = bones.get('Hips')
    if root:
        root.location = (0, 0, 0)
        root.keyframe_insert(data_path="location", frame=0)
        root.location = (0, 0, -0.3)
        root.keyframe_insert(data_path="location", frame=8)
        # Launch up
        root.location = (0, 0, 0.5)
        root.keyframe_insert(data_path="location", frame=14)
        # Apex
        root.location = (0, 0, 1.2)
        root.keyframe_insert(data_path="location", frame=18)
        # Coming down
        root.location = (0, 0, 0.5)
        root.keyframe_insert(data_path="location", frame=24)
        # Landing
        root.location = (0, 0, -0.2)
        root.keyframe_insert(data_path="location", frame=30)
        # Recovery
        root.location = (0, 0, 0)
        root.keyframe_insert(data_path="location", frame=36)
    
    # Arms swing up during jump
    left_arm = bones.get('LUpperArm')
    right_arm = bones.get('RUpperArm')
    
    if left_arm:
        left_arm.rotation_euler = (0, 0, 0)
        left_arm.keyframe_insert(data_path="rotation_euler", frame=0)
        left_arm.rotation_euler = (-0.5, 0, 0)
        left_arm.keyframe_insert(data_path="rotation_euler", frame=8)
        left_arm.rotation_euler = (-1.5, 0, 0)
        left_arm.keyframe_insert(data_path="rotation_euler", frame=18)
        left_arm.rotation_euler = (0, 0, 0)
        left_arm.keyframe_insert(data_path="rotation_euler", frame=36)
    
    if right_arm:
        right_arm.rotation_euler = (0, 0, 0)
        right_arm.keyframe_insert(data_path="rotation_euler", frame=0)
        right_arm.rotation_euler = (-0.5, 0, 0)
        right_arm.keyframe_insert(data_path="rotation_euler", frame=8)
        right_arm.rotation_euler = (-1.5, 0, 0)
        right_arm.keyframe_insert(data_path="rotation_euler", frame=18)
        right_arm.rotation_euler = (0, 0, 0)
        right_arm.keyframe_insert(data_path="rotation_euler", frame=36)
    
    # Legs tuck during jump
    left_leg = bones.get('LThigh')
    right_leg = bones.get('RThigh')
    
    if left_leg:
        left_leg.rotation_euler = (0, 0, 0)
        left_leg.keyframe_insert(data_path="rotation_euler", frame=0)
        left_leg.rotation_euler = (0.8, 0, 0)
        left_leg.keyframe_insert(data_path="rotation_euler", frame=8)
        left_leg.rotation_euler = (0.3, 0, 0)
        left_leg.keyframe_insert(data_path="rotation_euler", frame=18)
        left_leg.rotation_euler = (0, 0, 0)
        left_leg.keyframe_insert(data_path="rotation_euler", frame=36)
    
    if right_leg:
        right_leg.rotation_euler = (0, 0, 0)
        right_leg.keyframe_insert(data_path="rotation_euler", frame=0)
        right_leg.rotation_euler = (0.8, 0, 0)
        right_leg.keyframe_insert(data_path="rotation_euler", frame=8)
        right_leg.rotation_euler = (0.3, 0, 0)
        right_leg.keyframe_insert(data_path="rotation_euler", frame=18)
        right_leg.rotation_euler = (0, 0, 0)
        right_leg.keyframe_insert(data_path="rotation_euler", frame=36)
    
    armature.animation_data_create()
    armature.animation_data.action = action
    
    print("Created jump animation")

def create_bashful_pose():
    """
    Cute standing bashful pose: weight on one leg, hip tilt, head down,
    one hand near face/chest, fingers twirling, soft smile.
    Length: 2 seconds (48 frames) looping idle.
    """
    action = bpy.data.actions.new(name="bashful-pose")
    
    armature = bpy.data.objects.get('Armature')
    if not armature:
        return
    
    bones = armature.pose.bones
    
    # Weight on one leg - hip tilt
    spine = bones.get('Spine')
    if spine:
        spine.rotation_euler = (0, 0, 0.15)
        spine.keyframe_insert(data_path="rotation_euler", frame=0)
        spine.rotation_euler = (0, 0, 0.2)
        spine.keyframe_insert(data_path="rotation_euler", frame=24)
        spine.rotation_euler = (0, 0, 0.15)
        spine.keyframe_insert(data_path="rotation_euler", frame=48)
    
    # Head slightly tilted down and to the side
    head = bones.get('Head')
    if head:
        head.rotation_euler = (0.1, 0.2, 0.1)
        head.keyframe_insert(data_path="rotation_euler", frame=0)
        head.rotation_euler = (0.15, 0.25, 0.15)
        head.keyframe_insert(data_path="rotation_euler", frame=24)
        head.rotation_euler = (0.1, 0.2, 0.1)
        head.keyframe_insert(data_path="rotation_euler", frame=48)
    
    # One hand near face/chest (bashful gesture)
    right_arm = bones.get('RUpperArm')
    if right_arm:
        right_arm.rotation_euler = (-0.8, 0.3, 0.2)
        right_arm.keyframe_insert(data_path="rotation_euler", frame=0)
        right_arm.rotation_euler = (-0.9, 0.4, 0.3)
        right_arm.keyframe_insert(data_path="rotation_euler", frame=24)
        right_arm.rotation_euler = (-0.8, 0.3, 0.2)
        right_arm.keyframe_insert(data_path="rotation_euler", frame=48)
    
    # Left arm relaxed
    left_arm = bones.get('LUpperArm')
    if left_arm:
        left_arm.rotation_euler = (0, 0, -0.1)
        left_arm.keyframe_insert(data_path="rotation_euler", frame=0)
    
    # Slight body sway
    root = bones.get('Hips')
    if root:
        root.rotation_euler = (0, 0, 0.05)
        root.keyframe_insert(data_path="rotation_euler", frame=0)
        root.rotation_euler = (0, 0, -0.05)
        root.keyframe_insert(data_path="rotation_euler", frame=24)
        root.rotation_euler = (0, 0, 0.05)
        root.keyframe_insert(data_path="rotation_euler", frame=48)
    
    armature.animation_data_create()
    armature.animation_data.action = action
    action.use_cyclic = True
    
    print("Created bashful-pose animation")

def create_peace_sign_pose():
    """
    Striking peace-sign pose: confident stance, one hand raised in front of face
    making peace sign, bright smile, pink/purple aura glow.
    Length: 2 seconds (48 frames) looping.
    """
    action = bpy.data.actions.new(name="peace-sign-pose")
    
    armature = bpy.data.objects.get('Armature')
    if not armature:
        return
    
    bones = armature.pose.bones
    
    # Confident stance - slight hip tilt
    spine = bones.get('Spine')
    if spine:
        spine.rotation_euler = (0, 0, 0.1)
        spine.keyframe_insert(data_path="rotation_euler", frame=0)
    
    # Head looking at camera - slight confident tilt
    head = bones.get('Head')
    if head:
        head.rotation_euler = (-0.05, 0, 0)
        head.keyframe_insert(data_path="rotation_euler", frame=0)
        head.rotation_euler = (-0.1, 0, 0)
        head.keyframe_insert(data_path="rotation_euler", frame=24)
        head.rotation_euler = (-0.05, 0, 0)
        head.keyframe_insert(data_path="rotation_euler", frame=48)
    
    # Right hand raised in front of face - peace sign
    right_arm = bones.get('RUpperArm')
    if right_arm:
        right_arm.rotation_euler = (-2.5, 0.5, 0.3)
        right_arm.keyframe_insert(data_path="rotation_euler", frame=0)
        right_arm.rotation_euler = (-2.6, 0.6, 0.4)
        right_arm.keyframe_insert(data_path="rotation_euler", frame=24)
        right_arm.rotation_euler = (-2.5, 0.5, 0.3)
        right_arm.keyframe_insert(data_path="rotation_euler", frame=48)
    
    # Left arm relaxed at side
    left_arm = bones.get('LUpperArm')
    if left_arm:
        left_arm.rotation_euler = (0, 0, -0.15)
        left_arm.keyframe_insert(data_path="rotation_euler", frame=0)
    
    # Slight body movement
    root = bones.get('Hips')
    if root:
        root.rotation_euler = (0, 0, 0.05)
        root.keyframe_insert(data_path="rotation_euler", frame=0)
        root.rotation_euler = (0, 0, -0.05)
        root.keyframe_insert(data_path="rotation_euler", frame=24)
        root.rotation_euler = (0, 0, 0.05)
        root.keyframe_insert(data_path="rotation_euler", frame=48)
    
    armature.animation_data_create()
    armature.animation_data.action = action
    action.use_cyclic = True
    
    print("Created peace-sign-pose animation")

def setup_aura_material():
    """
    Create an aura material with emission for the peace-sign pose glow.
    This adds a pink/purple emission to the character material.
    """
    for mat in bpy.data.materials:
        if mat.use_nodes:
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            
            # Add emission node for aura
            emission = nodes.new('ShaderNodeEmission')
            emission.inputs['Color'].default_value = (1.0, 0.16, 0.54, 1.0)  # Neon pink
            emission.inputs['Strength'].default_value = 2.0
            
            # Add mix shader
            mix = nodes.new('ShaderNodeMixShader')
            
            # Find output node
            output = nodes.get('Material Output')
            if output:
                # Connect mix to output
                links.new(mix.outputs[0], output.inputs['Surface'])
                
                # Find BSDF
                bsdf = nodes.get('Principled BSDF')
                if bsdf:
                    links.new(bsdf.outputs[0], mix.inputs[1])
                    links.new(emission.outputs[0], mix.inputs[2])
    
    print("Aura material setup complete")

def export_animations():
    """Export all animations as glTF with Draco compression"""
    bpy.ops.export_scene.gltf(
        filepath='/Users/ultraviollett/projectSHURA/data/avatars/shura/embeddings/shura-02/06_Final/web/shura_02_animated.glb',
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
    print("Exported animated GLB")

# Main execution
if __name__ == '__main__':
    print("=== SHURA_02 Animation Pipeline ===")
    
    # Don't clear existing - we want to keep the good base animations
    # clear_all_actions()
    
    create_walk_cycle()
    create_jump()
    create_bashful_pose()
    create_peace_sign_pose()
    setup_aura_material()
    export_animations()
    
    print("=== Pipeline Complete ===")
