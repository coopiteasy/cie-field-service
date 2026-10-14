# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    available_worker_ids = fields.Many2many(
        "fsm.person",
        "fsm_order_available_workers_rel",
        compute="_compute_available_workers",
        help="Workers available based on skills and working hours.",
    )

    @api.depends(
        "skill_worker_ids",
        "scheduled_date_start",
        "scheduled_duration",
        "scheduled_date_end",
    )
    def _compute_available_workers(self):
        for order in self:
            workers = order.skill_worker_ids
            start = order.scheduled_date_start
            end = order.scheduled_date_end
            if start and end:
                workers = workers.filtered(
                    lambda w, s=start, e=end: w.is_available_for_dates(s, e)
                )
                order.available_worker_ids = workers
            else:
                order.available_worker_ids = False
