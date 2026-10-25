# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    fsm_person_ids = fields.One2many(
        comodel_name="fsm.person",
        inverse_name="partner_id",
        readonly=True,
    )

    fsm_person_id = fields.Many2one(
        comodel_name="fsm.person",
        string="Related FS Person",
        compute="_compute_fsm_person_id",
        readonly=True,
    )

    @api.depends("fsm_person_ids")
    def _compute_fsm_person_id(self):
        for partner in self:
            partner.fsm_person_id = partner.fsm_person_ids[:1]
