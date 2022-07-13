# Copyright 2022 ELITE Advanced technologies.
# Copyright 2022 ELITE - Salim ROUMILI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from datetime import timedelta
from odoo import fields, models
from odoo.exceptions import UserError, ValidationError
import requests
from requests.exceptions import HTTPError
import logging

_logger = logging.getLogger(__name__)


class HrJob(models.Model):
    _inherit = 'hr.job'

    flatchr_job_id = fields.Char(string='Flatchr job ID')  # unique ID generated by Flatchr
    reference = fields.Char(string='Reference')
    description = fields.Html(string='Description')
    experience = fields.Integer(string='Experience')
    salary = fields.Integer(string='Salary')
    contract_type_id = fields.Many2one("hr.contract.type", string='Contract type')
    education_level_id = fields.Many2one("hr.education.level", string='Education level')
    activity_id = fields.Many2one("hr.activity", string='Activity')
    channel_id = fields.Many2one("hr.channel", string='Channel')
    metier_id = fields.Many2one("hr.metier", string='Metier')
    mensuality = fields.Selection([("y", "annuel"), ("m", "mensuel"), ("h", "horaire")], "Mensuality", default="m")
    driver_license = fields.Boolean(string='Driver license')
    remote = fields.Boolean(string='Remote')
    handicap = fields.Boolean(string='Handicap')
    partial = fields.Boolean(string='Partial')

    @staticmethod
    def get_odoo_id(env, field_name, field_value, field_id):
        model_name = 'hr.' + field_name.replace('_', '.')
        res_id = env[model_name].search([('flatchr_id', '=', field_id)])

        vals = {
            'flatchr_id': field_id,
            'name': field_value
        }

        if not res_id:
            res_id = env[model_name].create(vals)
        else:
            res_id.write(vals)

        return res_id.id

    def parse_vacancy(self, vacancy_dict: dict) -> dict:
        existing_job_id = self.env['hr.job'].search([('flatchr_job_id', '=', vacancy_dict['id'])])

        content_dict = {
            'flatchr_job_id': vacancy_dict['id'],
            'name': vacancy_dict['title'],
            'reference': vacancy_dict['reference'],
            'description': vacancy_dict['description'] + vacancy_dict['mission'] + vacancy_dict['profile'],
            'experience': vacancy_dict['experience'],
            'salary': vacancy_dict['salary'],
            'contract_type_id': self.get_odoo_id(self.env, 'contract_type', vacancy_dict['contract_type'], vacancy_dict['contract_type_id']),
            'education_level_id': self.get_odoo_id(self.env, 'education_level', vacancy_dict['education_level'], vacancy_dict['education_level_id']),
            'activity_id': self.get_odoo_id(self.env, 'activity', vacancy_dict['activity'], vacancy_dict['activity_id']),
            'channel_id': self.get_odoo_id(self.env, 'channel', vacancy_dict['channel'], vacancy_dict['channel_id']),
            'metier_id': self.get_odoo_id(self.env, 'metier', vacancy_dict['metier'], vacancy_dict['metier_id']),
            'mensuality': vacancy_dict['mensuality'],
            'driver_license': vacancy_dict['driver_license'],
            'remote': vacancy_dict['remote'],
            'handicap': vacancy_dict['handicap'],
            'partial': vacancy_dict['partial'],
            #'state': 'recruit' if vacancy_dict['status'] == 1 else 'open',
        }

        if not existing_job_id:
            vacancy_id = self.env['hr.job'].create(content_dict)
        else:
            vacancy_id = existing_job_id[0]
            vacancy_id.write(content_dict)

        self.env.cr.execute("UPDATE hr_job SET create_date = '%s' WHERE id = %s" %(vacancy_dict['created_at'], vacancy_id.id))

        return vacancy_id

    def parse_applicant(self, applicant: dict, vacancy_ids):
        company_key = self.env['ir.config_parameter'].sudo().get_param('flatchr_connector.flatchr_company_key')
        token = self.env['ir.config_parameter'].sudo().get_param('flatchr_connector.flatchr_token')
        flatchr_candidate_id = applicant['applicant']
        url = f'https://api.flatchr.io/company/{company_key}/applicant/{flatchr_candidate_id}?fields=candidate,vacancy,candidate.consent'
        headers = requests.structures.CaseInsensitiveDict()
        headers['Authorization'] = f'Bearer {token}'
        headers['Content-Type'] = 'application/json'
        response = requests.get(url, headers=headers)
        job_id = False

        if response.status_code  == 200:
            job_id = vacancy_ids.search([("flatchr_job_id", "=", response.json()['vacancy_id'])], limit=1)

        if job_id:
            content_dict = {
                'flatchr_applicant_id': applicant['applicant'],
                'name': f"{applicant['firstname']} {applicant['lastname']} (Flatchr)",
                'email': applicant['email'],
                'phone': applicant['phone'],
            }

            existing_partners = self.env['res.partner'].search([('flatchr_applicant_id', '=', applicant['applicant'])])
            if not existing_partners:
                partner_id = self.env['res.partner'].create(content_dict)
            else:
                partner_id = existing_partners[0]
                partner_id.write(content_dict)

            # Then we can take care of the hr_applicant
            if applicant['vacancy']:
                content_dict = {
                    'name': f"{applicant['firstname'].upper()} {applicant['lastname'].upper()}",
                    'partner_name': f"{applicant['firstname'].upper()} {applicant['lastname'].upper()}",
                    'flatchr_applicant_id': applicant['applicant'],
                    'date_source': datetime.now(),
                    'partner_id': partner_id.id,
                    'applicant_source': applicant['source'],
                    'job_id': job_id.id,

                    'secteur_ids': [(4, job_id.activity_id.id)],
                    'filiere_ids': [(4, job_id.channel_id.id)],
                    'metier_ids': [(4, job_id.metier_id.id)],
                }

                existing_applicants = self.env['hr.applicant'].search([('flatchr_applicant_id', '=', applicant['applicant'])])

                if not existing_applicants:
                    hr_applicant_id = self.env['hr.applicant'].sudo().create(content_dict)
                    hr_applicant_id.user_id = False

                    self.env.cr.execute("UPDATE hr_applicant SET create_date = '%s' WHERE id = %s" %(str(datetime.strptime(applicant['created_at'], "%d/%m/%y")), hr_applicant_id.id))
                #else:
                #    hr_applicant_id = existing_applicants[0]
                #    hr_applicant_id.write(content_dict)
        #else:
        #    raise ValidationError("Job %s not found !" % applicant['vacancy'])

    def fetch_flatchr_data(self):
        date_start = datetime.now()
        _logger.info("******* Début de la synchronisation Flatchr %s" % date_start)

        slug = self.env['ir.config_parameter'].sudo().get_param('flatchr_connector.flatchr_enterprise_slug')
        api_key = self.env['ir.config_parameter'].sudo().get_param('flatchr_connector.flatchr_api_key')
        token = self.env['ir.config_parameter'].sudo().get_param('flatchr_connector.flatchr_token')
        company_key = self.env['ir.config_parameter'].sudo().get_param('flatchr_connector.flatchr_company_key')
        last_sync_date = self.env['ir.config_parameter'].sudo().get_param('flatchr_connector.last_sync_date')
        sync_period = self.env['ir.config_parameter'].sudo().get_param('flatchr_connector.sync_period')
        # Retrieve and parse jobs
        headers = requests.structures.CaseInsensitiveDict()
        headers['Authorization'] = f'Bearer {token}'
        headers['Content-Type'] = 'application/json'

        vacancy_ids = self.env['hr.job']  # Those silly goobers don't know how to reference records properly using ids, so I have to identify them DIY-style using a title.
        try:
            response = requests.get(f'https://careers.flatchr.io/company/{slug}.json', headers={'Accept': '*/*', 'Authorization': f'Bearer {token}'})
            response.raise_for_status()

        except HTTPError as http_err:
            raise ValidationError('HTTP error occurred: %s' %http_err)

        i = 0
        for vacancy in response.json()['items']:
            if vacancy['vacancy']:
                vacancy_ids += self.parse_vacancy(vacancy['vacancy'])
                i = i + 1

        archived_vacancy_ids = self.env['hr.job'].search([('state', 'not in', ['open']),('id', 'not in', vacancy_ids.ids)])
        #for vacancy_id in archived_vacancy_ids:
        #    vacancy_id.active_ela = False

        # Retrieve and parse applicants
        url = f'https://api.flatchr.io/company/{company_key}/search/applicants?fields=candidate,vacancy,candidate.consent'
        start_from = datetime.strptime(last_sync_date, '%Y-%m-%d') - timedelta(days=int(sync_period))
        #end_from = datetime.strptime(last_sync_date, '%Y-%m-%d')
        #data = f'{{"start": "{start_from}", "end":"{end_from}"}}'
        data = f'{{"start": "{start_from}"}}'

        response = requests.post(url, headers=headers, data=data)
        
        j = 0
        for applicant in response.json():
            self.parse_applicant(applicant, vacancy_ids)
            j = j + 1
            if j % 200 == 0:
                self.env.cr.commit()

        self.env['ir.config_parameter'].sudo().set_param('flatchr_connector.last_sync_date', datetime.now().date())
        _logger.info("******* Fin de la synchronisation Flatchr %s" % datetime.now())
        _logger.info("******* %s Annonces et %s Candidats synchronisés en %s" % (i, j, datetime.now() - date_start))

    #def set_recruit(self):
    #    for record in self:
    #        applicant_ids = self.env['hr.applicant'].with_context(active_test=False).search([("job_id", "=", record.id)])
    #        #_logger.info("******* Fin de la synchronisation Flatchr %s" % applicant_ids)***
    #        applicant_ids.set_recruit()

    #    return super(HrJob, self).set_recruit()

    #def set_open(self):
    #    for record in self:
    #        applicant_ids = self.env['hr.applicant'].search([("job_id", "=", record.id)])
    #        applicant_ids.write({'refuse_reason_id': 1, 'active': False})

    #    return super(HrJob, self).set_open()
