from pydantic import BaseModel, Field


class ProcessMeetingRequest(BaseModel):
    """Request DTO for POST /meeting/process."""

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
