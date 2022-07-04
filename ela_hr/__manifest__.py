# Copyright 2022 ELITE Advanced technologies.
# Copyright 2022 ELITE - Salim ROUMILI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Ela hr",
    "summary": """
        This module provides extension of hr functionalities.
        """,
    'category': 'Human Resources/Employees',
    'sequence': 199,
    "summary": "Extend employee information",
    "version": "15.0.0.0.0",
    "author": "ELITE Advanced technologies",
    "depends": [
        "base",
        "web",
        "calendar",
        "hr",
        "hr_recruitment",
        "hr_recruitment_survey",
        "project",
        "crm",
        "mail",
        "phone_validation",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/duplicate_user_id_wizard.xml",
        "views/hr_applicant_view.xml",
        "views/hr_job_view.xml",
        "views/project_task_view.xml",
        "views/hr_applicant_tags_view.xml",
        "views/hr_applicant_objects_view.xml",
        "views/hr_recruitment_stage_view.xml",
        "views/project_task_type_view.xml",
        "views/calendar_event_view.xml",
        "views/web_calendar_templates.xml",
        "views/crm_lead_view.xml",
        "views/hr_applicant_crm_view.xml",
        "views/hr_applicant_crm_stage_view.xml",
        "views/res_users_view.xml",
        "views/res_partner_view.xml",
        "views/mail_activity_views.xml",
        "views/mail_activity_type_views.xml",
        "security/security.xml",
        "data/ir_cron.xml",
    ],
    "qweb": [
    ],
    'assets': {
        'web.assets_backend': [
            'ela_hr/static/src/css/styles.css',
            'ela_hr/static/src/components/activity/activity_mark_done_popover.scss',
        ],
        'web.assets_common': [
            'ela_hr/static/src/models/activity/activity.js',
            'ela_hr/static/src/components/activity/activity.js',
        ],
        'web.assets_qweb': [
            'ela_hr/static/src/components/activity/activity.xml',
            'ela_hr/static/src/components/mail_template/mail_template.xml',
        ],
    },
    "license": "AGPL-3",
    "installable": True,
    "application": True,
}
