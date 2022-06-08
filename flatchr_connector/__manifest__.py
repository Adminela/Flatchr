{
    "name": "Flatchr Connector",
    "summary": """
        This module provides a connector to the Flatchr API.
        It regularly fetches new job offers and candidates from Flatchr in
        order to ingest them in your Odoo database.
        """,
    "category": "",
    "version": "15.0.1.0.0",
    "author": "ELITE Advanced technologies",
    "website": "http://www.odoo.com",
    "license": "OEEL-1",
    "depends": [
        'hr_recruitment',
        'contacts',
    ],
    "data": [
        "data/ir_cron.xml",
        "views/hr_applicant.xml",
        "views/hr_job.xml",
        "views/res_partner_view.xml",
        "views/res_config_settings.xml",
        "wizard/csv_dl_wizard.xml",
        "security/ir.model.access.csv"
    ],
}
