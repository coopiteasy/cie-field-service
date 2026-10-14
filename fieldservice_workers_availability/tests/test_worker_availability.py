# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import datetime

from pytz import UTC

from odoo import Command
from odoo.tests.common import TransactionCase


class TestWorkerAvailability(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        attendance_vals = []
        for day in range(5):
            attendance_vals.append(
                (
                    0,
                    0,
                    {
                        "name": f"Day {day} Morning",
                        "dayofweek": str(day),
                        "hour_from": 8.0,
                        "hour_to": 12.0,
                        "day_period": "morning",
                    },
                )
            )
            attendance_vals.append(
                (
                    0,
                    0,
                    {
                        "name": f"Day {day} Afternoon",
                        "dayofweek": str(day),
                        "hour_from": 13.0,
                        "hour_to": 17.0,
                        "day_period": "afternoon",
                    },
                )
            )

        cls.fixed_calendar = cls.env["resource.calendar"].create(
            {
                "name": "Fixed Brussels",
                "tz": "Europe/Brussels",
                "attendance_ids": attendance_vals,
            }
        )

        cls.flexible_calendar = cls.env["resource.calendar"].create(
            {
                "name": "Flexible Brussels",
                "tz": "Europe/Brussels",
                "flexible_hours": True,
                "hours_per_day": 8.0,
                "full_time_required_hours": 40.0,
            }
        )

        cls.worker_fixed = cls.env["fsm.person"].create(
            {
                "name": "Fixed Worker",
                "calendar_id": cls.fixed_calendar.id,
            }
        )
        cls.worker_flexible = cls.env["fsm.person"].create(
            {
                "name": "Flexible Worker",
                "calendar_id": cls.flexible_calendar.id,
            }
        )
        cls.worker_no_calendar = cls.env["fsm.person"].create(
            {"name": "No Calendar Worker"}
        )

    # Jan 15, 2025 is a Wednesday. Brussels = UTC+1 in January.
    # Working hours: 8:00-17:00 Brussels = 7:00-16:00 UTC

    def test_fixed_available_during_working_hours(self):
        start = datetime(2025, 1, 15, 8, 0, 0, tzinfo=UTC)
        end = datetime(2025, 1, 15, 9, 0, 0, tzinfo=UTC)
        self.assertTrue(self.worker_fixed.is_available_for_dates(start, end))

    def test_fixed_unavailable_outside_working_hours(self):
        start = datetime(2025, 1, 15, 17, 0, 0, tzinfo=UTC)
        end = datetime(2025, 1, 15, 18, 0, 0, tzinfo=UTC)
        self.assertFalse(self.worker_fixed.is_available_for_dates(start, end))

    def test_fixed_unavailable_on_weekend(self):
        start = datetime(2025, 1, 18, 9, 0, 0, tzinfo=UTC)
        end = datetime(2025, 1, 18, 10, 0, 0, tzinfo=UTC)
        self.assertFalse(self.worker_fixed.is_available_for_dates(start, end))

    def test_fixed_unavailable_during_leave(self):
        self.env["resource.calendar.leaves"].create(
            {
                "name": "Sick Leave",
                "calendar_id": self.fixed_calendar.id,
                "date_from": datetime(2025, 1, 15, 8, 0, 0),
                "date_to": datetime(2025, 1, 15, 9, 0, 0),
                "resource_id": False,
                "time_type": "leave",
            }
        )
        start = datetime(2025, 1, 15, 8, 0, 0, tzinfo=UTC)
        end = datetime(2025, 1, 15, 9, 0, 0, tzinfo=UTC)
        self.assertFalse(self.worker_fixed.is_available_for_dates(start, end))

    def test_flexible_available_outside_normal_hours(self):
        start = datetime(2025, 1, 15, 17, 0, 0, tzinfo=UTC)
        end = datetime(2025, 1, 15, 18, 0, 0, tzinfo=UTC)
        self.assertTrue(self.worker_flexible.is_available_for_dates(start, end))

    def test_flexible_unavailable_during_leave(self):
        self.env["resource.calendar.leaves"].create(
            {
                "name": "Sick Leave",
                "calendar_id": self.flexible_calendar.id,
                "date_from": datetime(2025, 1, 15, 8, 0, 0),
                "date_to": datetime(2025, 1, 15, 9, 0, 0),
                "resource_id": False,
                "time_type": "leave",
            }
        )
        start = datetime(2025, 1, 15, 8, 0, 0, tzinfo=UTC)
        end = datetime(2025, 1, 15, 9, 0, 0, tzinfo=UTC)
        self.assertFalse(self.worker_flexible.is_available_for_dates(start, end))

    def test_no_calendar_unavailable(self):
        start = datetime(2025, 1, 15, 8, 0, 0, tzinfo=UTC)
        end = datetime(2025, 1, 15, 9, 0, 0, tzinfo=UTC)
        self.assertFalse(self.worker_no_calendar.is_available_for_dates(start, end))

    def test_compute_available_worker_ids(self):
        owner = self.env["res.partner"].create({"name": "Test Owner"})
        location = self.env["fsm.location"].create(
            {"name": "Test Loc", "owner_id": owner.id}
        )

        skill_type = self.env["hr.skill.type"].create({"name": "Technical"})
        skill_level = self.env["hr.skill.level"].create(
            {"name": "Beginner", "skill_type_id": skill_type.id}
        )
        skill = self.env["hr.skill"].create(
            {"name": "Repair", "skill_type_id": skill_type.id}
        )
        self.env["fsm.person.skill"].create(
            {
                "person_id": self.worker_fixed.id,
                "skill_id": skill.id,
                "skill_level_id": skill_level.id,
                "skill_type_id": skill_type.id,
            }
        )

        order = self.env["fsm.order"].create(
            {
                "location_id": location.id,
                "scheduled_date_start": "2025-01-15 08:00:00",
                "scheduled_date_end": "2025-01-15 09:00:00",
            }
        )
        order.skill_ids = [Command.set([skill.id])]

        self.assertEqual(order.available_worker_ids, self.worker_fixed)
