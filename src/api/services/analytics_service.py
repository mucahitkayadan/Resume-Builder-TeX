from typing import Optional
from datetime import datetime
from src.core.database.factory import get_unit_of_work

class AnalyticsService:
    def __init__(self):
        self.uow = get_unit_of_work()

    async def get_application_metrics(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ):
        with self.uow:
            applications = self.uow.applications.get_by_date_range(
                user_id, start_date, end_date
            )
            
            # Calculate metrics
            total = len(applications)
            status_breakdown = {}
            response_times = []
            companies = {}
            positions = {}
            salaries = []

            for app in applications:
                # Status breakdown
                status = app.status
                status_breakdown[status] = status_breakdown.get(status, 0) + 1

                # Company and position stats
                companies[app.company_name] = companies.get(app.company_name, 0) + 1
                positions[app.job_title] = positions.get(app.job_title, 0) + 1

                # Response time and salary stats
                if app.application_date and app.updated_at:
                    response_time = (app.updated_at - app.application_date).days
                    response_times.append(response_time)

                if app.salary_range:
                    avg_salary = (app.salary_range.get('min', 0) + app.salary_range.get('max', 0)) / 2
                    salaries.append(avg_salary)

            return {
                "total_applications": total,
                "status_breakdown": status_breakdown,
                "success_rate": len([a for a in applications if a.status == 'accepted']) / total if total > 0 else 0,
                "average_response_time": sum(response_times) / len(response_times) if response_times else 0,
                "applications_by_company": companies,
                "applications_by_position": positions,
                "salary_range_stats": {
                    "average": sum(salaries) / len(salaries) if salaries else 0,
                    "min": min(salaries) if salaries else 0,
                    "max": max(salaries) if salaries else 0
                }
            }

    async def get_user_activity(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ):
        with self.uow:
            resumes = self.uow.resumes.get_by_date_range(user_id, start_date, end_date)
            cover_letters = self.uow.cover_letters.get_by_date_range(user_id, start_date, end_date)
            documents = self.uow.documents.get_by_date_range(user_id, start_date, end_date)

            # Calculate activity metrics
            activity_timeline = []
            templates_used = {}

            for doc in documents:
                if doc.template_id:
                    templates_used[doc.template_id] = templates_used.get(doc.template_id, 0) + 1

            return {
                "total_resumes_generated": len(resumes),
                "total_cover_letters_generated": len(cover_letters),
                "documents_by_type": {
                    "resume": len(resumes),
                    "cover_letter": len(cover_letters),
                    "other": len(documents) - len(resumes) - len(cover_letters)
                },
                "activity_timeline": activity_timeline,
                "most_used_templates": dict(sorted(
                    templates_used.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5])
            } 