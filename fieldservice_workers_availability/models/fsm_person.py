# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime

import pytz

from odoo import models


class FSMPerson(models.Model):
    _inherit = "fsm.person"

    def is_available_for_dates(self, start: datetime, end: datetime):
        self.ensure_one()
        start = start.replace(tzinfo=pytz.UTC)
        end = end.replace(tzinfo=pytz.UTC)

        calendar = self.calendar_id
        if not calendar:
            return False

        # _unavailable_intervals will not return anything for durations of 0
        if start == end:
            end += datetime.timedelta(seconds=1)

        unavailable = calendar._unavailable_intervals(start, end)
        return not any(
            unavailable_start <= end
            and unavailable_end >= start
            and unavailable_start < unavailable_end
            for unavailable_start, unavailable_end in unavailable
        )

    def action_assign_to_order(self):
        self.ensure_one()
        order_id = self.env.context.get("fsm_order_id")
        if order_id:
            self.env["fsm.order"].browse(order_id).person_id = self
