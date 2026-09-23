import bpy
import math

# Import
bpy.ops.import_scene.gltf(filepath='/Users/ultraviollett/projectSHURA/data/avatars/shura/embeddings/shura-02/04_Rig/shura_02_rigged.glb')

# Find EMPTY bones
def find_empty(name):
    return bpy.data.objects.get(name)

def set_keyframe(obj, frame, location=None, rotation=None):
    if location is not None:
        obj.location = location
        obj.keyframe_insert(data_path="location", frame=frame)
    if rotation is not None:
        obj.rotation_euler = rotation
        obj.keyframe_insert(data_path="rotation_euler", frame=frame)

# Create actions by animating EMPTY bones directly
def create_walk_cycle():
    action = bpy.data.actions.new(name="walk-cycle")
    
    hips = find_empty('Hips')
    spine = find_empty('Spine')
    head = find_empty('Head')
    l_arm = find_empty('LUpperArm') or find_empty('LShoulder')
    r_arm = find_empty('RUpperArm') or find_empty('RShoulder')
    l_leg = find_empty('LThigh')
    r_leg = find_empty('RThigh')
    
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
    
    # Assign to Armature EMPTY
    armature = find_empty('Armature')
    if armature:
        armature.animation_data_create()
        armature.animation_data.action = action
        action.use_cyclic = True
    
    print("Created walk-cycle")

def create_jump():
    action = bpy.data.actions.new(name="jump")
    
    hips = find_empty('Hips')
    l_arm = find_empty('LUpperArm') or find_empty('LShoulder')
    r_arm = find_empty('RUpperArm') or find_empty('RShoulder')
    l_leg = find_empty('LThigh')
    r_leg = find_empty('RThigh')
    
    if hips:
        set_keyframe(hips, 0, location=(0, 0, 0))
        set_keyframe(hips, 8, location=(0, 0, -0.3))
        set_keyframe(hips, 14, location=(0, 0, 0.5))
        set_keyframe(hips, 18, location=(0, 0, 1.2))
        set_keyframe(hips, 24, location=(0, 0, 0.5))
        set_keyframe(hips, 30, location=(0, 0, -0.2))
        set_keyframe(hips, 36, location=(0, 0, 0))
    
    for frame, rot in [(0, (0,0,0)), (8, (-0.5,0,0)), (18, (-1.5,0,0)), (36, (0,0,0))]:
        if l_arm: set_keyframe(l_arm, frame, rotation=rot)
        if r_arm: set_keyframe(r_arm, frame, rotation=rot)
    
    for frame, rot in [(0, (0,0,0)), (8, (0.8,0,0)), (18, (0.3,0,0)), (36, (0,0,0))]:
        if l_leg: set_keyframe(l_leg, frame, rotation=rot)
        if r_leg: set_keyframe(r_leg, frame, rotation=rot)
    
    armature = find_empty('Armature')
    if armature:
        armature.animation_data_create()
        armature.animation_data.action = action
    
    print("Created jump")

def create_bashful_pose():
    action = bpy.data.actions.new(name="bashful-pose")
    
    spine = find_empty('Spine')
    head = find_empty('Head')
    r_arm = find_empty('RUpperArm') or find_empty('RShoulder')
    l_arm = find_empty('LUpperArm') or find_empty('LShoulder')
    hips = find_empty('Hips')
    
    for frame, sway in [(0, 0.15), (24, 0.2), (48, 0.15)]:
        if spine: set_keyframe(spine, frame, rotation=(0, 0, sway))
    
    for frame, tilt in [(0, (0.1, 0.2, 0.1)), (24, (0.15, 0.25, 0.15)), (48, (0.1, 0.2, 0.1))]:
        if head: set_keyframe(head, frame, rotation=tilt)
    
    for frame, rot in [(0, (-0.8, 0.3, 0.2)), (24, (-0.9, 0.4, 0.3)), (48, (-0.8, 0.3, 0.2))]:
        if r_arm: set_keyframe(r_arm, frame, rotation=rot)
    
    if l_arm: set_keyframe(l_arm, 0, rotation=(0, 0, -0.1))
    
    for frame, sway in [(0, (0,0,0.05)), (24, (0,0,-0.05)), (48, (0,0,0.05))]:
        if hips: set_keyframe(hips, frame, rotation=sway)
    
    armature = find_empty('Armature')
    if armature:
        armature.animation_data_create()
        armature.animation_data.action = action
        action.use_cyclic = True
    
    print("Created bashful-pose")

def create_peace_sign_pose():
    action = bpy.data.actions.new(name="peace-sign-pose")
    
    spine = find_empty('Spine')
    head = find_empty('Head')
    r_arm = find_empty('RUpperArm') or find_empty('RShoulder')
    l_arm = find_empty('LUpperArm') or find_empty('LShoulder')
    hips = find_empty('Hips')
    
    if spine: set_keyframe(spine, 0, rotation=(0, 0, 0.1))
    
    for frame, rot in [(0, (-0.05, 0, 0)), (24, (-0.1, 0, 0)), (48, (-0.05, 0, 0))]:
        if head: set_keyframe(head, frame, rotation=rot)
    
    for frame, rot in [(0, (-2.5, 0.5, 0.3)), (24, (-2.6, 0.6, 0.4)), (48, (-2.5, 0.5, 0.3))]:
        if r_arm: set_keyframe(r_arm, frame, rotation=rot)
    
    if l_arm: set_keyframe(l_arm, 0, rotation=(0, 0, -0.15))
    
    for frame, rot in [(0, (0,0,0.05)), (24, (0,0,-0.05)), (48, (0,0,0.05))]:
        if hips: set_keyframe(hips, frame, rotation=rot)
    
    armature = find_empty('Armature')
    if armature:
        armature.animation_data_create()
        armature.animation_data.action = action
        action.use_cyclic = True
    
    print("Created peace-sign-pose")

def add_aura():
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
    # Push actions to NLA tracks on Armature EMPTY
    armature = find_empty('Armature')
    if armature and armature.animation_data:
        for action in bpy.data.actions:
            if action.use_cyclic or action == armature.animation_data.action:
                track = armature.animation_data.nla_tracks.new()
                track.strips.new(action.name, 0, action)
                track.name = action.name
    
    bpy.ops.export_scene.gltf(
        filepath='/Users/ultraviollett/projectSHURA/data/avatars/shura/embeddings/shura-02/06_Final/web/shura_02_v1_prototype.glb',
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
    print("Exported")

print("=== SHURA_02 Pipeline ===")
create_walk_cycle()
create_jump()
create_bashful_pose()
create_peace_sign_pose()
add_aura()
export_glb()
print("=== COMPLETE ===")
