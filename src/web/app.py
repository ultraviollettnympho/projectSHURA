from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Optional
import shutil
import os
from pathlib import Path
from src.core.config import BrainConfig
from src.core.brain import AIVtuberBrain
from src.utils.logger import get_logger

logger = get_logger("bea.web")

app = FastAPI(title="AI Vtuber Brain API")

# cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# global brain instance
brain_instance: Optional[AIVtuberBrain] = None

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)

    @field_validator("message")
    @classmethod
    def strip_message(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("message cannot be empty or whitespace-only")
        return stripped

class ConfigUpdateRequest(BaseModel):
    config: Dict[str, Any]

def get_brain() -> AIVtuberBrain:
    if not brain_instance:
        raise HTTPException(status_code=503, detail="Brain not initialized")
    return brain_instance

@app.get("/config")
def get_config():
    brain = get_brain()
    # eeturn as dict
    from dataclasses import asdict
    return asdict(brain.config)

@app.post("/config")
def update_config(request: ConfigUpdateRequest):
    brain = get_brain()
    try:
        current_tts = brain.config.tts_provider
        current_stt = brain.config.stt_provider
        restart_required = False

        # uppdate config object
        for key, value in request.config.items():
            if hasattr(brain.config, key):
                setattr(brain.config, key, value)
                
                # check for critical changes
                if key == "tts_provider" and value != current_tts:
                    restart_required = True
                if key == "stt_provider" and value != current_stt:
                    restart_required = True
        
        # save to file
        brain.config.save_to_file()
        
        # hot reload
        brain.reload_configuration()
        
        msg = "Configuration updated."
        if restart_required:
            msg += " RESTART REQUIRED to apply new provider settings."
            
        return {
            "status": "success", 
            "message": msg,
            "restart_required": restart_required
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
def get_history():
    brain = get_brain()
    return brain.history_manager.get_recent_history(limit=50)

@app.get("/sessions")
def list_sessions():
    brain = get_brain()
    return brain.list_sessions()

@app.post("/sessions")
async def create_session():
    brain = get_brain()
    session_id = brain.create_new_session()
    return {"status": "success", "session_id": session_id}

@app.post("/sessions/{session_id}/activate")
async def activate_session(session_id: str):
    brain = get_brain()
    if brain.load_session(session_id):
        return {"status": "success", "message": f"Session {session_id} activated"}
    raise HTTPException(status_code=404, detail="Session not found")

@app.post("/memory/save")
async def save_memory():
    brain = get_brain()
    if not brain.memory_skill:
        raise HTTPException(status_code=400, detail="Memory skill not initialized")
        
    if brain.memory_skill.save_current_session():
        return {"status": "success", "message": "Memory saving triggered."}
    else:
        return {"status": "error", "message": "Could not save memory (Skill disabled or empty session)."}

@app.get("/status")
def get_status():
    brain = get_brain()
    active_skills = []
    if brain.skill_registry is not None:
        active_skills = [
            skill.skill_name for skill in brain.skill_registry.toggleable()
            if skill.active and skill.skill_name is not None
        ]
    return {
        "is_speaking": brain.is_speaking,
        "is_sleeping": brain.is_sleeping,
        "active_skills": active_skills
    }

@app.post("/dream/run")
async def run_dream():
    """Put Bea to sleep and run a consolidation (dream) pass, then wake her."""
    brain = get_brain()
    result = await brain.run_dream()
    return {"status": "success" if result.get("ok") else "error", "result": result}

@app.post("/dream/wake")
async def wake_bea():
    brain = get_brain()
    brain.wake_up()
    return {"status": "success", "is_sleeping": brain.is_sleeping}

@app.get("/dream/projection")
def dream_projection(run_id: Optional[str] = None):
    """Stable read-only projection of Dream Engine state for the Command Center / UI.

    This endpoint consumes the Dream domain through the projection layer
    (src/core/dream/projection.py) and the existing EventManager replay.
    It does NOT reach into consciousness, expression, avatar PNG, OBS,
    or provider internals directly. Mutation of Dream state must go
    through /dream/run (explicit command), not through this endpoint.
    """
    brain = get_brain()
    from src.core.dream.projection import DreamStateProjection, build_projection
    from src.core.dream.domain import DreamRun, DreamState
    # Application boundary: projection reads only. Domain mutation is
    # routed explicitly through DreamSkill / /dream/run.
    domain_run = DreamRun(run_id=run_id or "unknown", state=DreamState.CREATED)
    proj = build_projection(
        run=domain_run,
        event_manager=brain.event_manager,
        snapshot=None,
    )
    return proj.to_dict()


@app.get("/forge/state")
def forge_state(run_id: Optional[str] = None):
    """Aggregate semantic state for the FORGE frontend/avatar layer.

    Delegates to brain.get_forge_state() — the brain owns the projection
    construction, not the web layer. This endpoint is read-only; it does
    not mutate any state.

    Consumes:
      - PresenceRuntime (current presence state, emotion, motion)
      - AtlasService.snapshot() (active project, work items, milestones, decisions)
      - DreamStateProjection (dream run state, concepts, threads)
      - EventManager (recent events for activity feed)

    Produces ForgeState: a single semantic, renderer-agnostic object that any
    frontend or avatar renderer can consume. Contains NO PNG paths, OBS scene
    names, Live2D model indexes, UI coordinates, CSS state, or renderer-
    specific animation instructions.

    Mutation of any underlying state must go through explicit endpoints
    (/atlas/*, /dream/run, /skills/{name}/toggle) — not through this endpoint.
    """
    brain = get_brain()
    return brain.get_forge_state()


@app.get("/atlas/snapshot")
def atlas_snapshot():
    """Read-only ATLAS domain snapshot for the FORGE frontend / ATLAS tooling.

    Returns the current project, work item, milestone, decision, and artifact
    registry. This endpoint is read-only; mutations go through the /atlas/*
    endpoints below.
    """
    brain = get_brain()
    if brain.atlas_service is None:
        raise HTTPException(status_code=503, detail="ATLAS service not initialized")
    return brain.atlas_service.snapshot().to_dict()


@app.post("/atlas/projects")
def atlas_create_project(name: str = Form(...), description: str = Form(default="")):
    """Create a new ATLAS project."""
    brain = get_brain()
    if brain.atlas_service is None:
        raise HTTPException(status_code=503, detail="ATLAS service not initialized")
    project = brain.atlas_service.create_project(name=name, description=description)
    return {"status": "success", "project": _project_to_dict(project)}


@app.get("/atlas/projects")
def atlas_list_projects():
    brain = get_brain()
    if brain.atlas_service is None:
        raise HTTPException(status_code=503, detail="ATLAS service not initialized")
    return {"projects": [_project_to_dict(p) for p in brain.atlas_service.list_projects()]}


@app.get("/atlas/projects/{project_id}")
def atlas_get_project(project_id: str):
    brain = get_brain()
    if brain.atlas_service is None:
        raise HTTPException(status_code=503, detail="ATLAS service not initialized")
    try:
        return _project_to_dict(brain.atlas_service.get_project(project_id))
    except KeyError:
        raise HTTPException(status_code=404, detail="Project not found")


@app.post("/atlas/projects/{project_id}/active")
def atlas_set_active_project(project_id: str):
    brain = get_brain()
    if brain.atlas_service is None:
        raise HTTPException(status_code=503, detail="ATLAS service not initialized")
    try:
        project = brain.atlas_service.set_active_project(project_id)
        return {"status": "success", "active_project": _project_to_dict(project)}
    except KeyError:
        raise HTTPException(status_code=404, detail="Project not found")


@app.post("/atlas/projects/{project_id}")
def atlas_update_project(project_id: str, description: Optional[str] = Form(default=None),
                         name: Optional[str] = Form(default=None)):
    brain = get_brain()
    if brain.atlas_service is None:
        raise HTTPException(status_code=503, detail="ATLAS service not initialized")
    try:
        kwargs = {}
        if description is not None:
            kwargs["description"] = description
        if name is not None:
            kwargs["name"] = name
        project = brain.atlas_service.update_project(project_id, **kwargs)
        return {"status": "success", "project": _project_to_dict(project)}
    except KeyError:
        raise HTTPException(status_code=404, detail="Project not found")


@app.post("/atlas/projects/{project_id}/delete")
def atlas_delete_project(project_id: str):
    brain = get_brain()
    if brain.atlas_service is None:
        raise HTTPException(status_code=503, detail="ATLAS service not initialized")
    try:
        brain.atlas_service.delete_project(project_id)
        return {"status": "success"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Project not found")


@app.post("/atlas/projects/{project_id}/work-items")
def atlas_create_work_item(
    project_id: str,
    title: str = Form(...),
    description: str = Form(default=""),
    priority: str = Form(default="medium"),
    work_type: str = Form(default="task"),
    assigned_to: str = Form(default=""),
    depends_on: str = Form(default=""),
):
    brain = get_brain()
    if brain.atlas_service is None:
        raise HTTPException(status_code=503, detail="ATLAS service not initialized")
    try:
        deps = [d.strip() for d in depends_on.split(",") if d.strip()] if depends_on else []
        item = brain.atlas_service.create_work_item(
            project_id=project_id,
            title=title,
            description=description,
            priority=priority,
            work_type=work_type,
            assigned_to=assigned_to,
            depends_on=deps or None,
        )
        return {"status": "success", "work_item": _work_item_to_dict(item)}
    except KeyError:
        raise HTTPException(status_code=404, detail="Project not found")


@app.get("/atlas/projects/{project_id}/work-items")
def atlas_list_work_items(project_id: str, status: Optional[str] = None):
    brain = get_brain()
    if brain.atlas_service is None:
        raise HTTPException(status_code=503, detail="ATLAS service not initialized")
    try:
        brain.atlas_service.get_project(project_id)  # verify exists
    except KeyError:
        raise HTTPException(status_code=404, detail="Project not found")
    items = brain.atlas_service.list_work_items(project_id=project_id, status=status)
    return {"work_items": [_work_item_to_dict(w) for w in items]}


@app.post("/atlas/work-items/{item_id}/transition")
def atlas_transition_work_item(item_id: str, new_status: str = Form(...)):
    brain = get_brain()
    if brain.atlas_service is None:
        raise HTTPException(status_code=503, detail="ATLAS service not initialized")
    try:
        item = brain.atlas_service.transition_work_item(item_id, new_status)
        return {"status": "success", "work_item": _work_item_to_dict(item)}
    except KeyError:
        raise HTTPException(status_code=404, detail="Work item not found")


@app.get("/atlas/work-items/{item_id}")
def atlas_get_work_item(item_id: str):
    brain = get_brain()
    if brain.atlas_service is None:
        raise HTTPException(status_code=503, detail="ATLAS service not initialized")
    try:
        return _work_item_to_dict(brain.atlas_service.get_work_item(item_id))
    except KeyError:
        raise HTTPException(status_code=404, detail="Work item not found")


@app.post("/atlas/milestones")
def atlas_create_milestone(
    project_id: str = Form(...),
    name: str = Form(...),
    description: str = Form(default=""),
    order: int = Form(default=0),
):
    brain = get_brain()
    if brain.atlas_service is None:
        raise HTTPException(status_code=503, detail="ATLAS service not initialized")
    try:
        ms = brain.atlas_service.create_milestone(
            project_id=project_id, name=name,
            description=description, order=order,
        )
        return {"status": "success", "milestone": _milestone_to_dict(ms)}
    except KeyError:
        raise HTTPException(status_code=404, detail="Project not found")


@app.get("/atlas/milestones")
def atlas_list_milestones(project_id: Optional[str] = None):
    brain = get_brain()
    if brain.atlas_service is None:
        raise HTTPException(status_code=503, detail="ATLAS service not initialized")
    ms = brain.atlas_service.list_milestones(project_id=project_id)
    return {"milestones": [_milestone_to_dict(m) for m in ms]}


@app.post("/atlas/milestones/{milestone_id}/complete")
def atlas_complete_milestone(milestone_id: str):
    brain = get_brain()
    if brain.atlas_service is None:
        raise HTTPException(status_code=503, detail="ATLAS service not initialized")
    try:
        ms = brain.atlas_service.complete_milestone(milestone_id)
        return {"status": "success", "milestone": _milestone_to_dict(ms)}
    except KeyError:
        raise HTTPException(status_code=404, detail="Milestone not found")


@app.post("/atlas/decisions")
def atlas_record_decision(
    project_id: str = Form(...),
    title: str = Form(...),
    context: str = Form(default=""),
    decision: str = Form(default=""),
    consequences: str = Form(default=""),
    decided_by: str = Form(default=""),
):
    brain = get_brain()
    if brain.atlas_service is None:
        raise HTTPException(status_code=503, detail="ATLAS service not initialized")
    try:
        d = brain.atlas_service.record_decision(
            project_id=project_id, title=title, context=context,
            decision=decision, consequences=consequences, decided_by=decided_by,
        )
        return {"status": "success", "decision": _decision_to_dict(d)}
    except KeyError:
        raise HTTPException(status_code=404, detail="Project not found")


@app.get("/atlas/decisions")
def atlas_list_decisions(project_id: Optional[str] = None):
    brain = get_brain()
    if brain.atlas_service is None:
        raise HTTPException(status_code=503, detail="ATLAS service not initialized")
    ds = brain.atlas_service.list_decisions(project_id=project_id)
    return {"decisions": [_decision_to_dict(d) for d in ds]}


@app.post("/atlas/artifacts")
def atlas_add_artifact(
    project_id: str = Form(...),
    name: str = Form(...),
    kind: str = Form(default="file"),
    location: str = Form(default=""),
    description: str = Form(default=""),
):
    brain = get_brain()
    if brain.atlas_service is None:
        raise HTTPException(status_code=503, detail="ATLAS service not initialized")
    try:
        a = brain.atlas_service.add_artifact(
            project_id=project_id, name=name, kind=kind,
            location=location, description=description,
        )
        return {"status": "success", "artifact": _artifact_to_dict(a)}
    except KeyError:
        raise HTTPException(status_code=404, detail="Project not found")


@app.get("/atlas/artifacts")
def atlas_list_artifacts(project_id: Optional[str] = None):
    brain = get_brain()
    if brain.atlas_service is None:
        raise HTTPException(status_code=503, detail="ATLAS service not initialized")
    as_ = brain.atlas_service.list_artifacts(project_id=project_id)
    return {"artifacts": [_artifact_to_dict(a) for a in as_]}


@app.post("/atlas/artifacts/{artifact_id}/delete")
def atlas_remove_artifact(artifact_id: str):
    brain = get_brain()
    if brain.atlas_service is None:
        raise HTTPException(status_code=503, detail="ATLAS service not initialized")
    try:
        brain.atlas_service.remove_artifact(artifact_id)
        return {"status": "success"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Artifact not found")


# --- ATLAS/FORGE helper serializers ---

def _project_to_dict(p) -> dict:
    return {
        "project_id": p.project_id,
        "name": p.name,
        "description": p.description,
        "status": p.status,
        "created_at": p.created_at,
        "updated_at": p.updated_at,
        "metadata": p.metadata,
    }


def _work_item_to_dict(w) -> dict:
    return {
        "item_id": w.item_id,
        "project_id": w.project_id,
        "title": w.title,
        "description": w.description,
        "status": w.status,
        "priority": w.priority,
        "work_type": w.work_type,
        "depends_on": w.depends_on,
        "assigned_to": w.assigned_to,
        "created_at": w.created_at,
        "updated_at": w.updated_at,
        "completed_at": w.completed_at,
        "metadata": w.metadata,
    }


def _milestone_to_dict(m) -> dict:
    return {
        "milestone_id": m.milestone_id,
        "project_id": m.project_id,
        "name": m.name,
        "description": m.description,
        "status": m.status,
        "target_date": m.target_date,
        "order": m.order,
        "created_at": m.created_at,
        "updated_at": m.updated_at,
        "completed_at": m.completed_at,
    }


def _decision_to_dict(d) -> dict:
    return {
        "decision_id": d.decision_id,
        "project_id": d.project_id,
        "title": d.title,
        "context": d.context,
        "decision": d.decision,
        "consequences": d.consequences,
        "status": d.status,
        "decided_at": d.decided_at,
        "decided_by": d.decided_by,
        "supersedes": d.supersedes,
        "metadata": d.metadata,
    }


def _artifact_to_dict(a) -> dict:
    return {
        "artifact_id": a.artifact_id,
        "project_id": a.project_id,
        "name": a.name,
        "kind": a.kind,
        "location": a.location,
        "description": a.description,
        "created_at": a.created_at,
    }



# --- ATLAS service wiring on the brain --- (deprecated: ATLAS is now
# initialized at brain.initialize() time, not lazily via this endpoint.)
# The _wire_atlas_service function and lazy initialization pattern are
# replaced by brain.initialize() AtlasService creation. The /atlas/init
# endpoint is kept for backward compatibility as a status check.


@app.post("/atlas/init")
def atlas_init():
    """ATLAS service status check.

    ATLAS is now initialized at brain.initialize() time, not lazily via
    this endpoint. This endpoint is kept for backward compatibility and
    returns the current ATLAS service status.
    """
    brain = get_brain()
    service = brain.atlas_service
    if service is None:
        return {"status": "not_initialized", "message": "ATLAS not available"}
    return {
        "status": "ok",
        "message": "ATLAS service active (initialized at brain startup)",
        "project_count": len(service.list_projects()),
        "active_project_id": service._active_project_id if hasattr(service, "_active_project_id") else None,
    }

@app.get("/workspace/dream-events")
def workspace_dream_events(run_id: Optional[str] = None, limit: int = 50):
    """Workspace observation endpoint: Dream lifecycle events for workspace framework.
    Uses existing EventManager replay (subsystem='dream') through projection/event interfaces.
    Read-only observation only — mutation must route through /dream/run or application services.
    Bounded workspace adapter: connects workspace framework (`docs/design/COMMAND_CENTER_V1.md`)
    to verified event/projection framework (`docs/EVENT_CONTRACT.md`, `tests/test_events.py`).
    """
    brain = get_brain()
    events = brain.event_manager.replay(subsystem="dream", run_id=run_id) if run_id else brain.event_manager.replay(subsystem="dream")
    # Apply workspace-oriented presentation: include only structured fields; never infer state from messages
    result = [
        {
            "event_id": ev.get("event_id"),
            "event_type": ev.get("event_type"),
            "run_id": ev.get("run_id"),
            "subsystem": ev.get("subsystem"),
            "source": ev.get("source"),
            "message": ev.get("message"),
            "severity": ev.get("severity"),
            "visibility": ev.get("visibility"),
            "payload_summary": {k: v for k, v in (ev.get("payload") or {}).items() if isinstance(v, (str, int, float, bool, list))},
        }
        for ev in events[-limit:]
    ]
    return {"workspace_events": result}

@app.post("/chat")
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    brain = get_brain()
    
    # 1. generate text
    mood, message = await brain.generate_response(request.message)
    
    # 2. schedule output
    background_tasks.add_task(brain.perform_output_task, mood, message)
    
    return {
        "status": "success", 
        "response": {
            "role": "assistant",
            "content": message,
            "mood": mood
        }
    }

@app.post("/interrupt")
async def interrupt_speech():
    brain = get_brain()
    # execute interruption
    await brain.interrupt()
    return {"status": "success", "message": "Interrupted"}

@app.post("/audio")
async def upload_audio(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    brain = get_brain()
    
    # save temp file
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    filename = file.filename or "audio_upload.wav"
    temp_file = temp_dir / filename
    
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # process
    mood, message, transcript = await brain.generate_audio_response(str(temp_file))
    
    # schedule output
    background_tasks.add_task(brain.perform_output_task, mood, message)
    
    # cleanup
    if temp_file.exists():
        os.remove(temp_file)
        
    return {
        "status": "success", 
        "response": {
            "role": "assistant",
            "content": message,
            "mood": mood,
            "user_transcript": transcript
        }
    }

class DiscordChatRequest(BaseModel):
    username: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1, max_length=4000)
    channelId: str = "unknown"
    userId: Optional[str] = None
    messageId: Optional[str] = None
    isDm: bool = False

    @field_validator("message")
    @classmethod
    def strip_message(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("message cannot be empty or whitespace-only")
        return stripped

@app.post("/discord/chat")
async def discord_chat(request: DiscordChatRequest):
    brain = get_brain()

    logger.info(f"Discord Chat from {request.username}: {request.message}")

    # one mind: deposit a perception and return immediately. Bea answers on her
    # own via the discord tools (reply/send_message), not via a synchronous reply.
    brain.perceive_discord_text(
        request.message, request.username, request.channelId,
        message_id=request.messageId, user_id=request.userId, is_dm=request.isDm,
    )
    return {"status": "perceived"}

@app.post("/discord/audio")
async def discord_audio_interaction(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    username: str = Form(...),
    flush_buffer: str = Form(default="false"),
    user_id: Optional[str] = Form(default=None),
):
    brain = get_brain()

    # save temp file
    temp_dir = Path("temp_discord")
    temp_dir.mkdir(exist_ok=True)
    temp_file = temp_dir / f"{username}_{int(os.times().elapsed)}.wav"

    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # process
        status, text_response, transcript, audio_bytes = await brain.process_discord_interaction(str(temp_file), username, user_id=user_id)
        
        # convert audio to base64
        import base64
        audio_b64 = ""
        if audio_bytes:
             audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        return {
            "status": status, # "success" or "resume"
            "text": text_response,
            "transcript": transcript,
            "audio_base64": audio_b64
        }
    except Exception as e:
        logger.error(f"Discord Audio Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # cleanup
        if temp_file.exists():
            os.remove(temp_file)

@app.post("/voice/transcript")
async def buffer_voice_transcript(
    file: UploadFile = File(...),
    username: str = Form(...),
    user_id: Optional[str] = Form(default=None)
):
    """
    Overheard speech: transcribes a short snippet and feeds it to the
    consciousness as a VOICE perception (steering), without waiting for a reply.
    Bea decides on her own whether it's worth reacting to.
    """
    brain = get_brain()

    # save temp file
    temp_dir = Path("temp_discord")
    temp_dir.mkdir(exist_ok=True)
    temp_file = temp_dir / f"buf_{username}_{int(os.times().elapsed)}.wav"

    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    transcript = ""
    try:
        if brain.stt:
            transcript = brain.stt.transcribe(str(temp_file))
            logger.info(f"Overheard: [{username}] '{transcript}'")

        if transcript and transcript.strip() and transcript != "[Unintelligible]":
            if brain.surface_registry is not None:
                voice = brain.surface_registry.get("voice:discord")
                if voice is not None and hasattr(voice, "perceive"):
                    getattr(voice, "perceive")(transcript, username, user_id=user_id)

        return {"status": "perceived", "transcript": transcript}
    except Exception as e:
        logger.error(f"Overheard transcript error: {e}")
        return {"status": "error", "transcript": "", "error": str(e)}
    finally:
        if temp_file.exists():
            os.remove(temp_file)

@app.get("/skills")
def list_skills():
    brain = get_brain()
    skills_data = {}
    if brain.skill_registry is not None:
        for skill in brain.skill_registry.toggleable():
            key = skill.skill_name
            if key is not None:
                skills_data[key] = {
                    "enabled": skill.enabled,
                    "config": brain.config.skills.get(key, {}),
                    "active": skill.active,
                }
    return skills_data

@app.post("/skills/{name}/toggle")
async def toggle_skill(name: str, enable: bool):
    brain = get_brain()
    if brain.skill_registry is None or not brain.skill_registry.get_by_key(name):
        raise HTTPException(status_code=404, detail="Skill not found")

    await brain.set_skill_enabled(name, enable)
    return {"status": "success", "enabled": enable}

@app.get("/skills/logs")
def get_skill_logs():
    brain = get_brain()
    # backward compatibility
    events = brain.event_manager.get_events(limit=100)
    return [
        {"timestamp": e["timestamp"], "skill": e["source"], "message": e["message"]}
        for e in events if e["category"] in ["skill", "thought", "error"]
    ]

@app.get("/events")
def get_events(limit: int = 50):
    brain = get_brain()
    return brain.event_manager.get_events(limit=limit)

@app.get("/health")
def health():
    return {"status": "ok"}

# mount static files
frontend_path = Path(__file__).parent / "frontend" / "dist"
if frontend_path.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_path / "assets")), name="assets")
else:
    logger.warning(f"Frontend build not found at {frontend_path}. Run 'npm run build' in src/web/frontend.")

# --- SPA CATCH-ALL ROUTE ---
from fastapi.responses import FileResponse

@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    # verify api route mismatch
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API Endpoint not found")

    # serve index.html
    if frontend_path.exists():
        return FileResponse(frontend_path / "index.html")
    return {"error": "Frontend not found"}
