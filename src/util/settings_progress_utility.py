"""
Progress Utility Service

A utility service for emitting staged progress data.
This is a mocked service that will be replaced later with actual implementation.
"""
import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from src.domain.constants.events import Events

logger = logging.getLogger(__name__)


class SettingsProgressUtility:
    def __init__(
        self,
        chat_history_service: None
    ):
        self.chat_history_service = chat_history_service
        self.progress_stages = self._get_progress_stages()
    
    def _replace_tenant_placeholder(self, text: str, tenant_id: Optional[str] = None) -> str:
        """Replace <tenant_id> placeholder with actual tenant_id or default value"""
        if not text:
            return text
        
        replacement = tenant_id if tenant_id else "Secure.com"
        return text.replace("<tenant_id>", replacement)
    
    def _get_progress_stages(self) -> List[Dict[str, Any]]:
        """Define the three progress stages with their configurations"""
        return [
            {
                "type": "setting-1",
                "heading": "Setting Up Your Workspace",
                "completion_mindy_heading": "",
                "completion_mindy_text": "Your Security Workspace is ready! Secure, personalized, and ready to support your daily operations.",
                "sub_settings": []
            },
            {
                "type": "setting-2", 
                "heading": "Setting Up Your Secure Vault",
                "completion_mindy_heading": "",
                "completion_mindy_text": "Your Secure Vault is now being created — a private, encrypted space just for you.\n\nThis is where all your API keys, credentials, and sensitive configurations will be stored. Only you — and no one else — can access it, not even our team.",
                "sub_settings": []
            },
            {
                "type": "setting-3",
                "heading": "Setting Basic Skills for AI Teammate",
                "completion_mindy_heading": "AI Teammate is now equipped with core skills",
                "completion_mindy_text": "We've configured your AI Teammate with essential skills — ready to assist, learn from your workflows, and execute actions securely within your workspace. These skills will evolve as your usage grows.",
                "note": "You can modify these skills later from AI Teammate configuration from <tenant_id>'s platform.",
                "sub_settings": [
                    {"text": "Data Retrieval from Complex Knowledge Graphs", "progress": 20},
                    {"text": "Data Analytics", "progress": 20},
                    {"text": "Continuous Learning from Human Execution", "progress": 20},
                    {"text": "Automated Workflow Execution", "progress": 20},
                    {"text": "Automated Integration of Tools", "progress": 20}
                ]
            }
        ]
    
    async def start_progress_simulation(
        self, 
        sio, 
        sid: str, 
        tenant_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> None:
        """
        Start the complete progress simulation for all stages
        
        Args:
            sio: SocketIO server instance
            sid: Socket ID for the client
            tenant_id: Optional tenant identifier
            session_id: Optional session identifier (will generate if not provided)
        """
        if not session_id:
            session_id = str(uuid.uuid4())
                
        try:
            for stage_index, stage in enumerate(self.progress_stages):
                await self._simulate_stage_progress(
                    sio=sio,
                    sid=sid,
                    session_id=session_id,
                    stage=stage,
                    stage_index=stage_index,
                    tenant_id=tenant_id
                )
                
                if stage_index < len(self.progress_stages) - 1:
                    await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"Error in progress simulation: {e}")
            await self._emit_error(sio, sid, f"Progress simulation failed: {str(e)}")
    
    async def _simulate_stage_progress(
        self,
        sio,
        sid: str,
        session_id: str,
        stage: Dict[str, Any],
        stage_index: int,
        tenant_id: Optional[str] = None
    ) -> None:
        """Simulate progress for a single stage"""
        
        # Get note if it exists in the stage
        note = stage.get("note")
        
        await self._emit_progress_update(
            sio=sio,
            sid=sid,
            session_id=session_id,
            stage_type=stage["type"],
            heading=stage["heading"],
            progress=10,
            sub_settings=self._get_initial_sub_settings(stage["sub_settings"]),
            tenant_id=tenant_id,
            note=note
        )
        
        progress_steps = [25, 50, 75, 90]
        for progress in progress_steps:
            await asyncio.sleep(0.8)
            
            sub_settings = self._update_sub_settings_progress(
                stage["sub_settings"], 
                progress
            )
            
            await self._emit_progress_update(
                sio=sio,
                sid=sid,
                session_id=session_id,
                stage_type=stage["type"],
                heading=stage["heading"],
                progress=progress,
                sub_settings=sub_settings,
                tenant_id=tenant_id,
                note=note
            )
        
        await asyncio.sleep(1)
        await self._emit_progress_update(
            sio=sio,
            sid=sid,
            session_id=session_id,
            stage_type=stage["type"],
            heading=stage["heading"],
            progress=100,
            sub_settings=self._get_completed_sub_settings(stage["sub_settings"]),
            tenant_id=tenant_id,
            note=note
        )
        await asyncio.sleep(1)
        heading = stage["completion_mindy_heading"]
        text = stage["completion_mindy_text"]
        combined_content = f"{heading}\n{text}" if heading and text else (heading or text or "")
        response_data = {
            "heading": heading,
            "text": text,
            "combined_content": combined_content,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        await self.chat_history_service.emit_assistant_message(
                    sio=sio,
                    event=Events.MINDY,
                    data=response_data,
                    sid=sid,
                    tenant_id=tenant_id,
                    extract_content_from="combined_content"
                )

    
    def _get_initial_sub_settings(self, sub_settings: List[Dict]) -> List[Dict]:
        """Get initial sub-settings with starting progress"""
        if not sub_settings:
            return []
        
        return [
            {
                "text": sub["text"],
                "progress": sub["progress"]
            }
            for sub in sub_settings
        ]
    
    def _update_sub_settings_progress(
        self, 
        sub_settings: List[Dict], 
        overall_progress: int
    ) -> List[Dict]:
        """Update sub-settings progress based on overall progress"""
        if not sub_settings:
            return []
        
        sub_progress = min(100, int(overall_progress * 1.1))
        
        return [
            {
                "text": sub["text"],
                "progress": sub_progress
            }
            for sub in sub_settings
        ]
    
    def _get_completed_sub_settings(self, sub_settings: List[Dict]) -> List[Dict]:
        """Get completed sub-settings with 100% progress"""
        if not sub_settings:
            return []
        
        return [
            {
                "text": sub["text"],
                "progress": 100
            }
            for sub in sub_settings
        ]
    
    async def _emit_progress_update(
        self,
        sio,
        sid: str,
        session_id: str,
        stage_type: str,
        heading: str,
        progress: int,
        sub_settings: List[Dict],
        tenant_id: Optional[str] = None,
        note: Optional[str] = None
    ) -> None:
        
        progress_data = {
            "id": session_id,
            "type": stage_type,
            "heading": heading,
            "overall-progress": progress,
            "sub-settings": sub_settings,
            "is_settings": True
        }
        
        # Add note if provided, with tenant_id replacement
        if note:
            progress_data["note"] = self._replace_tenant_placeholder(note, tenant_id)
        
        if tenant_id:
            progress_data["tenant_id"] = tenant_id
        
        progress_data["timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        try:
            await sio.emit(Events.MINDY, progress_data, to=sid)
            
        except Exception as e:
            logger.error(f"Failed to emit progress: {e}")
            raise
    
    async def _emit_error(self, sio, sid: str, error_message: str) -> None:
        """Emit an error message"""
        error_data = {
            "error": error_message,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        try:
            await sio.emit("errors", error_data, to=sid)
        except Exception as e:
            logger.error(f"Failed to emit error: {e}")


async def start_setting_progress(
    sio, 
    sid: str, 
    chat_history = None,
    tenant_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> None:
    utility = SettingsProgressUtility(chat_history)
    await utility.start_progress_simulation(
        sio=sio,
        sid=sid,
        tenant_id=tenant_id,
        session_id=session_id
    )
