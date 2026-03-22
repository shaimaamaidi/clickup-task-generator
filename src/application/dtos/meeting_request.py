"""Request DTOs for the meeting processing API."""

from pydantic import BaseModel, Field


class ProcessMeetingRequest(BaseModel):
    """Request payload for POST /meeting/process.

    Attributes:
        space_id: ClickUp space ID to sync tasks into.
        meeting_summary: Meeting summary in Arabic or French.
    """

    space_id: str = Field(
        ...,
        description="ClickUp space ID to sync tasks into",
        examples=["abc123xyz"],
    )
    meeting_summary: str = Field(
        ...,
        description="Meeting summary in Arabic or French",
        examples=["تم الاتفاق على تطوير نظام الإشعارات وإصلاح خطأ في التقويم."],
    )
