"""Status Tracker Agent Module.

Tracks application statuses, interview updates, and next actions for job applications with automation-ready hooks.

Author: Autonomous JobHunt System
Version: 1.0.0
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class StatusTracker:
    """
    Monitors statuses of job applications and records interview, feedback, and acceptance updates.
    Future: Add notification triggers and LLM-based next-action decisioning.
    """
    def __init__(self):
        self.applications: List[Dict[str,Any]] = []
        logger.info("StatusTracker initialized.")

    def add_application(self, job: Dict[str,Any], submitted_date: datetime=None):
        entry = {
            'job': job,
            'submitted_date': submitted_date if submitted_date else datetime.now(),
            'status': 'applied',
            'history': [('applied', datetime.now())]
        }
        self.applications.append(entry)
        logger.info("Added application for job '%s' at '%s'", job.get('title'), job.get('company'))

    def update_status(self, job: Dict[str,Any], status: str, note: str=None):
        for entry in self.applications:
            if entry['job'] == job:
                entry['status'] = status
                entry['history'].append((status, datetime.now(), note))
                logger.info("Updated status for '%s' to '%s'", job.get('title'), status)
                break

    def get_applications_by_status(self, status: str) -> List[Dict[str,Any]]:
        return [e['job'] for e in self.applications if e['status'] == status]

    def status_report(self) -> Dict[str,Any]:
        return {
            'total': len(self.applications),
            'status_counts': self._count_statuses(),
            'recent_updates': [self._summarize_entry(e) for e in self.applications[-5:]]
        }
    def _count_statuses(self) -> Dict[str,int]:
        c = {}
        for e in self.applications:
            c[e['status']] = c.get(e['status'],0) + 1
        return c
    def _summarize_entry(self, entry: Dict[str,Any]) -> Dict[str,Any]:
        return {
            'title': entry['job'].get('title'),
            'company': entry['job'].get('company'),
            'status': entry['status'],
            'last_update': entry['history'][-1][1].isoformat()
        }

    def history_for_job(self, job: Dict[str,Any]) -> List:
        for entry in self.applications:
            if entry['job'] == job:
                return entry['history']
        return []
    # TODO: Integrate with notification/alert systems for next steps/invitations
    # TODO: Use LLM to recommend follow-up actions, email templates, and reminders

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    tracker = StatusTracker()
    job1 = { 'title':'ML Engineer', 'company':'Tech Corp'}
    job2 = { 'title':'Developer', 'company':'StartUp Inc'}
    tracker.add_application(job1)
    tracker.add_application(job2)
    tracker.update_status(job1, 'interview', 'Interview scheduled for Monday')
    print('Status Report:', tracker.status_report())
    print('History for job1:', tracker.history_for_job(job1))
