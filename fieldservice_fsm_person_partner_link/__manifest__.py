# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Field Service - FSM Person Partner Link",
    "summary": "Provide links between fsm_person and related partner",
    "version": "18.0.1.0.0",
    "category": "Field Service",
    "website": "https://github.com/coopiteasy/cie-field-service",
    "author": "Coop IT Easy SC",
    "maintainers": ["mihien"],
    "license": "AGPL-3",
    "depends": [
        "fieldservice",
        "partner_social_service",
    ],
    "data": [
        "views/fsm_person.xml",
        "views/res_partner_views.xml",
    ],
}
