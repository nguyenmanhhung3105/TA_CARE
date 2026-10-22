"""Seasonal marketplace context and retired recruitment entry points."""
from odoo import fields
from .service_design import service_design_context


def marketplace_context(env):
    site = env['website'].sudo().search([('domain','ilike','khovieclam')],limit=1)
    jobs = env['hr.job'].sudo().search([('care_opportunity_kind','=','flexible'),
        ('website_id','=',site.id), ('tacare_status','=','published'), ('is_published','=',True),
        '|', ('tacare_deadline','=',False), ('tacare_deadline','>=',fields.Date.today())], order='write_date desc,id desc')
    categories = env['care.capability.category'].sudo().search([('code','!=','driving')],order='id')
    photos = {'cleaning':'cleaning','cooking':'cooking','garden':'garden','farm':'farm',
              'loading':'warehouse','repair':'tools','tutoring':'learning','digital':'digital','pets':'cat'}
    return {**service_design_context(categories, jobs), 'seasonal_jobs':jobs[:6], 'seasonal_job_count':len(jobs),
            'seasonal_categories':categories, 'seasonal_photos':photos,
            'seasonal_category_counts':{c.id:len(jobs.filtered(lambda j:j.flex_category_id==c)) for c in categories}}
