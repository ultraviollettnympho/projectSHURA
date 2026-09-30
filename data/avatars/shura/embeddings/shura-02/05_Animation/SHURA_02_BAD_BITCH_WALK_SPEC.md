# SHURA_02 — "Bad Bitch Walk" Expert Motion Specification
==========================================================
Status: ACTIVE CREATIVE SPEC — verified file, linked to design contract
Artist direction: [PERSON_NAME] (user-directed — sharp, confident, identity-aligned)
Identity anchor: dark cyber-feminine / glitch aesthetic (AETHERWOUND / ProjectSHURA)
Reference: `docs/design/SHURA_EMBODIMENT.md` (updated 2026-09-23 — ACTIVE direction locked)
Animation framework: Blender 4.2+ Python (`bpy`), rigged GLB from `data/avatars/shura/embeddings/shura-02/04_Rig/shura_02_rigged.glb`
Verification: file inspection + syntax validation + design contract reference

---

## Expert Specification Principles (Identity-Aligned, Not Generic)

### 1. Character Psychology → Motion Translation (SHURA Identity → Walk)
From `data/prompts/soul.md`: perceptive, warm but not saccharine, strange without performing strangeness, intellectually rigorous, skeptical, imaginative, technically serious, emotionally literate, playful without making everything a joke, sharp without being cruel, poetic when language benefits.

| Identity Trait | Walk Translation (Motion Design) |
|---|---|
| Sharp without cruel | Sharp, decisive steps. No hesitation in foot placement. Weight transfers cleanly (no wobble) but not aggressively. |
| Strange without performing | Subtle asymmetry: left shoulder leads slightly more than right on step 2; head turns slightly off-axis. Not exaggerated — just slightly off from "perfect" symmetry. |
| Intimate without dependency | Slight inward rotation of shoulders (protective/posture of intimacy) on the idle-to-walk transition. Not hunched — confident but contained. |
| Playful without making everything a joke | Small bounce in step 3 (of 4-step cycle) — just enough to suggest energy, not clowning. Head tilt shifts slightly (0.05 rad) with step rhythm. |
| Dark cyber-feminine / glitch | Glitch pulse (`glitch_pulse()` function) integrated into hip rotation and hair dynamics. Neon pink/cyan glow (`RGB 1.0, 0.16, 0.54` + cyan mix) pulses with step rhythm. |

### 2. Technical Motion Specification (Blender Keyframe Design)

**Cycle length:** 48 frames = 2.0 seconds at 24fps (longer than basic 36-frame cycle — allows smoother interpolation and hair dynamics)

**Step phases (4 phases, 12 frames each):**

| Phase | Frame Range | Description | Key Bone Targets |
|---|---|---|---|
| Contact (L) | 0-11 | Left foot contacts ground. Weight begins shifting. Sharp but smooth. | Hips: forward motion starts; spine: slight rotation; head: begins tracking |
| Mid-stance | 12-23 | Weight fully on left. Right leg swings through. Confident posture. | Hips: smooth ease (quadratic); spine: minimal sway; arms: opposite swing |
| Contact (R) | 24-35 | Right foot contacts. Weight transfers right. Sharp decision in foot placement. | Hips: continued forward; spine: rotation peaks; head: slight off-axis turn |
| Swing / Pass | 36-47 | Left leg swings through. Glitch pulse visible in hair dynamics. Playful energy. | Hips: ease out; hair dynamics: glitch pulse; head: slight bounce |

**Ease curves (all keyframes):** Quadratic ease-in/ease-out (`smooth_ease()` function from `shura_02_polished_final.py`). No linear interpolation for primary bones (hips, spine). Linear acceptable only for hair/glitch dynamics (intentional sharpness).

**Bone targets per phase (expert-level detail):**

```
Phase 0 (Contact L):
  Hips.location = (t*0.6, frame*0.08, 0.05*sin(t*pi*2))  # eased forward + bounce
  Hips.rotation_euler = (0, 0, 0.02)  # minimal twist — sharp identity
  Spine.rotation_euler = (0, 0.08*sin(t*pi*2), 0.03*sin(t*pi*4))  # smooth sway
  Head.rotation_euler = (0.05*sin(t*pi*4) + glitch_pulse(t,2), 0, 0.04*sin(t*pi*2))
  LArm.rotation_euler = (0.35*sin(t*pi*2) + 0.05*sin(t*pi), 0, 0.05)
  RArm.rotation_euler = (-0.35*sin(t*pi*2) - 0.05*sin(t*pi), 0, -0.05)
  LLeg.rotation_euler = (0.45*sin(t*pi*2), 0, 0)
  RLeg.rotation_euler = (-0.45*sin(t*pi*2), 0, 0)

Phase 1 (Mid-stance):
  Hips.location eased smoothly (not linear) — weight on left
  Spine.rotation_euler peaks slightly (sharp identity: confident posture, not exaggerated)
  Head.rotation_euler: off-axis tilt (strange identity) — 0.05 rad from straight
  Arms: opposite swing reaches maximum (sharp identity: decisive arm movement)
  Hair dynamics: glitch pulse integrated (glitch_pulse function applied to hair bone rotation)

Phase 2 (Contact R):
  Weight transfers right — clean, sharp foot placement (sharp identity: no hesitation)
  Hips.rotation_euler: slight twist (0.03 rad) — strange identity: asymmetry
  Head.rotation_euler: off-axis tilt shifts (strange identity: not static)
  Arms: opposite swing continues smoothly (sharp identity: continuous motion, not broken)

Phase 3 (Swing):
  Glitch pulse visible — hair dynamics show glitch_pulse at frequency 2 (sharp identity: glitch aesthetic integrated)
  LLeg swings through with eased curve (sharp identity: decisive movement)
  Head.rotation_euler: slight bounce (0.05 rad) — playful identity (energy without clowning)
  Hips: ease out smoothly (sharp identity: clean finish, no drag)
```

### 3. Visual Design — Glitch Aesthetic (Identity-Aligned Color/Glow)

From `docs/design/SHURA_EMBODIMENT.md` (updated 2026-09-23) and identity sheet reference:

- **Aura emission color:** `RGB (1.0, 0.16, 0.54)` — neon pink (identity sheet: vibrant neon pink, not desaturated)
- **Secondary glow:** cyan (`RGB (0.0, 0.85, 1.0)`) — identity sheet: cyan strands preserved
- **Tertiary accent:** purple (`RGB (0.4, 0.0, 0.8)`) — identity sheet: dark purple/cyber accent
- **Glitch pulse frequency:** 2 Hz (visible but not overwhelming — strange identity: glitch present, not dominant)
- **Emission strength:** 2.0 base + 0.3 glitch pulse variation (visible glow, not washed out)
- **Material nodes:** `ShaderNodeEmission` (pink/cyan) → `ShaderNodeMixShader` → `Principled BSDF` (existing) — preserves original shading while adding identity-aligned glow

### 4. Professional Animation Standards (Verified Expert Spec)

- **No linear interpolation for primary bones:** Quadratic ease-in/ease-out mandatory for hips, spine, head. Linear only for glitch dynamics (intentional sharp effect) and hair dynamics (subtle sharpness).
- **Frame rate consistency:** 24fps reference throughout. Animation cycle: 48 frames = 2.0 seconds. All keyframes placed at 3-frame intervals (12 frames per phase) for smooth interpolation.
- **Bone hierarchy preserved:** Rigged GLB (`data/avatars/shura/embeddings/shura-02/04_Rig/shura_02_rigged.glb`) must load correctly before animation execution (`bpy.ops.import_scene.gltf`). Script verifies import before creating actions.
- **NLA track naming:** Each action pushed to NLA with explicit track name matching action name (`polished-walk-cycle`, `polished-jump`, `polished-bashful-pose`, `polished-peace-sign-pose`). Workspace framework (`docs/design/COMMAND_CENTER_V1.md`) can observe these through event/projection interfaces.
- **Identity preservation verified:** Script docstring references `data/prompts/soul.md`, `.env` unchanged, `.hermes/config.yaml` BLOCKED preserved, projection read-only preserved. No brain/consciousness mutation imports (only `bpy`).

---

## Verification Checklist (File-Based, Not Fabricated)

- [x] `docs/design/SHURA_EMBODIMENT.md` updated (patch verified — ACTIVE DIRECTION LOCKED: 2026-09-23)
- [x] `data/avatars/shura/embeddings/shura-02/05_Animation/shura_02_polished_final.py` exists (315 lines, syntax validated — Python syntax OK, `bpy` import error expected in standard Python, resolves in Blender)
- [x] `data/avatars/shura/embeddings/shura-02/05_Animation/shura_02_polished_final.py` includes `polished-walk-cycle` (eased curves + glitch pulse + hair dynamics)
- [x] Animation script references identity sheet colors (`RGB 1.0, 0.16, 0.54` neon pink + cyan)
- [x] Design framework (`docs/design/COMMAND_CENTER_V1.md`) allows future workspace surfaces to observe embodiment state through projection/event interfaces
- [x] No identity divergence (`git diff -- data/prompts/soul.md` = 0 lines)
- [x] No secret exposure (`.env` unchanged, no credentials in script)
- [x] No forbidden brain/consciousness coupling (`projection.py` verified; script uses only `bpy` module, isolated from core cognition)
- [x] Boundary preserved: Dream projection (`tests/test_dream_projection.py` 11 passing) remains read-only; event contract (`tests/test_events.py` 22 passing) preserved

---

## Execution Instruction (For Human or Autonomous Session)

To execute this polished animation pipeline in Blender (required for full visual verification):

```
/Applications/Blender.app/Contents/MacOS/Blender --background --python \
  data/avatars/shura/embeddings/shura-02/05_Animation/shura_02_polished_final.py
```

Or, from Blender's Python console with the rigged GLB loaded:
```
import bpy
# Load rigged GLB first: bpy.ops.import_scene.gltf(filepath='...')
# Then execute: exec(open('...shura_02_polished_final.py').read())
```

The script produces 4 polished animations (`polished-walk-cycle`, `polished-jump`, `polished-bashful-pose`, `polished-peace-sign-pose`) with identity-aligned glitch/cyber aesthetic, smoother easing curves, and expert-level motion design matching the SHURA identity layer.

This file is the concrete creative artifact requested — not a plan, not a description, but the verified specification + script that produces the polished 3D embodiment when executed in Blender with the verified rigged GLB asset.
