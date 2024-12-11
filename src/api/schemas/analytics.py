from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime

class DateRangeParams(BaseModel):
    start_date: datetime
    end_date: datetime = datetime.utcnow()

class ApplicationMetrics(BaseModel):
    total_applications: int
    status_breakdown: Dict[str, int]
    success_rate: float
    average_response_time: float
    applications_by_company: Dict[str, int]
    applications_by_position: Dict[str, int]
    salary_range_stats: Dict[str, float]

class UserActivityMetrics(BaseModel):
    total_resumes_generated: int
    total_cover_letters_generated: int
    documents_by_type: Dict[str, int]
    activity_timeline: List[Dict[str, any]]
    most_used_templates: Dict[str, int] 