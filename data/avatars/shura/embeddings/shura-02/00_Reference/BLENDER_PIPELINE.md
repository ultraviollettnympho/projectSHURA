# SHURA_02 → Complete Blender 3D Character Pipeline
**For Hermes / Operator Guidance**  
**Character:** SHURA_02 (Project Shura)  
**Source of Truth:** SHURA Identity Sheet (anchored to latest full-body photo) + provided reference art  
**Goal:** Production-ready Blender character with clean topology, proper weight painting, and the following polished animations:

1. Smooth walking cycle  
2. Jumping  
3. Cute standing bashful pose (twirling fingers)  
4. Striking pose: peace sign in front of face, smiling, pink/purple aura glow  

**Target Software:** Blender 4.2+ (or latest LTS)  
**Primary Workflow:** Blender modeling + retopo + rigging → optional MetaHuman base if needed → Substance 3D Painter / Krita texturing → final animation & rendering  

---

## Phase 0 – Preparation (Do This First)

1. Load the **SHURA Identity Sheet** and the original full-body photo side-by-side.  
2. Lock the following as non-negotiable:
   - Height: 5'7" (170 cm)
   - Build: Slim / Athletic
   - Hair: Long layered black with distinct neon pink + cyan strands, high messy ponytail, volume and separation must be preserved
   - Face: Exact proportions, eye shape, piercings, makeup from photo
   - Outfit geometry: Oversized jacket (slouchy), cropped tank with star symbol, harness/shorts, asymmetrical stockings, chunky platform boots
   - Color separation: Neon pink, cyan, pure black, white/grey accents must stay vibrant and distinct
   - Markings/tattoos: Keep consistent across all views (star/compass symbols, graffiti tags)

3. Recommended folder structure:
```
SHURA_02/
├── 00_Reference/
│   ├── identity_sheet.png
│   ├── photo_anchor.png
│   └── detail_closeups/
├── 01_Sculpt/
├── 02_Retopo/
├── 03_UV_Texture/
├── 04_Rig/
├── 05_Animation/
└── 06_Final/
```

---

## Phase 1 – High-Resolution Sculpt / Base Mesh

**Option A (Recommended for pure stylized look):**  
Start from scratch in Blender or use a clean female base mesh (e.g., from BlenderKit or MakeHuman) scaled to 170 cm.

**Option B (Faster realism hybrid):**  
Use MetaHuman (or similar) as base → heavily restyle proportions, face, and outfit to match the identity sheet exactly.

### Steps:
1. Import identity sheet as reference images (front / side / back / 3/4).  
2. Block out body proportions first (head-to-body ratio, limb lengths, hip/shoulder width).  
3. Sculpt face last, constantly comparing to the photo anchor and close-up panels.  
4. Hair: Do **not** use particle hair yet. Model the main volumes as geometry or use a high-poly hair mesh that matches the layered look. Keep the pink/cyan strands as separate color groups.  
5. Outfit: Model the oversized jacket with proper thickness and folds. Keep the jacket, tank, shorts, harness, stockings, and boots as **separate objects** (or clearly marked vertex groups) so they can be textured and animated independently.  
6. Accessories: Model all chains, rings, buckles, piercings, and hanging straps as separate meshes.  
7. Apply Subdivision Surface + Multiresolution for detail, but plan for clean retopo later.

**Checkpoint:** Does the sculpt look identical to the photo when viewed from the same angle and lighting? If not, fix before moving on.

---

## Phase 2 – Retopology (Critical for Animation)

1. Create a clean, animation-friendly mesh:
   - Edge loops around eyes, mouth, joints, and clothing stress points.
   - Quads only (or majority quads).
   - Proper density: higher on face and hands, lower on body.
2. Transfer high-poly details via Shrinkwrap + Multires or Bake normals later.
3. Separate objects if needed:
   - Body
   - Hair (main + accent strands)
   - Jacket
   - Tank top
   - Shorts + harness
   - Stockings (left & right may differ)
   - Boots
   - Accessories (chains, piercings, etc.)

**Focus areas from identity sheet notes:**
- Hair volume & layered strands with color separation
- Outfit geometry (straps, buckles, chains, loose jacket)
- Facial features + piercings
- Boots with thick chunky soles
- Symmetry + intentional casual asymmetry

---

## Phase 3 – UV Unwrapping & Texturing

1. UV unwrap each object carefully. Use UDIM tiles if the character is high-detail.  
2. Texture in Substance 3D Painter (preferred) or Krita + Blender:  
   - Base colors strictly from the identity sheet palette (neon pink, cyan, black).  
   - Keep neon accents vibrant — do not desaturate.  
   - Jacket graffiti/tags must match the reference.  
   - Stockings: one fishnet, one solid with graffiti.  
   - Boots: metallic buckles + neon edge lighting.  
3. Create material slots for:
   - Skin (with subtle subsurface)
   - Hair (anisotropic or custom shader for neon strands)
   - Clothing (fabric + leather variants)
   - Metal (chains, rings, buckles)
   - Glow elements (star symbol, aura later)

Bake:
- Normal maps
- Ambient Occlusion
- Curvature / ID maps if needed

---

## Phase 4 – Rigging

1. Use Rigify or Auto-Rig Pro for a full biped rig.  
2. Add custom bones for:
   - Hair (main ponytail + secondary strands)
   - Jacket (so it can flop and follow body)
   - Harness straps and hanging chains (soft body or simple constraints)
   - Face (eye tracking, brow, mouth, tongue if needed for expressions)
3. Weight paint carefully:
   - Test extreme poses early.
   - Fix clothing clipping with corrective shape keys or mesh deform.
4. Create a simple control panel or use Rigify’s UI for easy posing.

**Optional but recommended:** Add a simple physics setup for the oversized jacket and long hair (soft body or cloth simulation with pin groups).

---

## Phase 5 – Animation Set (Exact Requests)

Create an Action library or NLA tracks for the following:

### 1. Smooth Walking Cycle
- Root motion or in-place cycle.
- Natural hip sway, arm swing, slight head bob.
- Jacket and hair should have secondary motion.
- Boots should plant firmly with weight transfer.
- Length: 1–2 second loop, easily blendable.

### 2. Jumping
- Anticipation → launch → apex → landing.
- Clean arc, proper knee bend on landing.
- Hair and jacket react with delayed secondary motion.
- Soft body / cloth helps here.

### 3. Cute Standing Bashful Pose (Twisting / Twirling Fingers)
- Standing weight on one leg, slight hip tilt.
- Head slightly tilted down or to the side, eyes looking up or away shyly.
- One hand near face or chest, fingers gently twirling / fidgeting.
- Soft smile or slight blush expression.
- Holdable pose (or short looping idle).

### 4. Striking Peace-Sign Pose + Aura
- Confident but cute stance.
- One hand raised in front of face making a clear peace sign (V-sign).
- Bright smile, eyes looking at camera.
- Pink + purple volumetric aura / glow surrounding the character.
  - Use a combination of:
    - Emission materials on a soft mesh shell or particles
    - Volume scatter / absorption for the aura
    - Bloom + glare in Compositor
    - Animated noise or soft pulse on the aura intensity
- Optional: subtle hair and jacket movement while holding the pose.

**Animation tips:**
- Use the Graph Editor for smooth, snappy, or soft curves as needed.
- Add secondary motion (hair, jacket, chains) on separate layers.
- Bake simulations where necessary for final export.

---

## Phase 6 – Polish & Final Output

1. Lighting: Match the neon cyberpunk mood of the reference (pink/cyan rim lights + soft key).  
2. Materials: Final shader tweaks for skin, hair anisotropy, fabric roughness, metal reflections.  
3. Compositor: Add subtle chromatic aberration, bloom, and the pink/purple aura glow.  
4. Export options:
   - .blend file with all actions
   - FBX / glTF for game engines
   - Alembic for simulations if needed
   - Rendered turntables + animation clips

**Final Checklist before delivery:**
- [ ] Matches identity sheet proportions and colors exactly  
- [ ] Clean topology, good deformation  
- [ ] All four requested animations polished and smooth  
- [ ] Aura present and glowing on the peace-sign pose  
- [ ] No clipping, no broken weights  
- [ ] Neon colors still vibrant  

---

## Recommended Tools Summary
- **Modeling / Retopo / Rig / Animate:** Blender 4.2+  
- **Texturing:** Substance 3D Painter (primary) or Krita  
- **Optional base:** MetaHuman (heavily restyled)  
- **Quick 2D → 3D experiments:** Hugging Face Spaces or similar (only for early concept tests)  
- **Physics:** Blender Cloth + Soft Body + Pin groups  

---

**This document is the complete operating manual.**  
Feed the identity sheet + this pipeline to Hermes and follow the phases in order. Every decision should be checked against the identity sheet as the single source of truth.

**Project Shura – SHURA_02**  
Ready for full 3D realization.
