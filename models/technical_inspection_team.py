# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import UserError
from odoo.tools.translate import _


class Team(models.Model):
    _name = 'technical_inspection.team'
    _inherit = ['mail.thread', 'ir.needaction_mixin', 'utm.mixin']

    @api.model
    @api.returns('self', lambda value: value.id if value else False)
    def _get_default_team_id(self, user_id=None):
        if not user_id:
            user_id = self.env.uid
        team_id = None
        if 'default_team_id' in self.env.context:
            team_id = self.env['technical_inspection.team'].browse(self.env.context.get('default_team_id'))
        if not team_id or not team_id.exists():
            team_id = self.env['technical_inspection.team'].sudo().search(
                ['|', ('user_id', '=', user_id), ('member_ids', '=', user_id)],
                limit=1)
        return team_id

    name = fields.Char('technical_inspection Team', required=True, index=True)
    active = fields.Boolean(default=True,
                            help="If the active field is set to false, it will allow you to hide the technical_inspection team without removing it.")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get('technical_inspection.team'))
    user_id = fields.Many2one('res.users', string='Team Leader')
    description = fields.Text('Description')
    assign_method = fields.Selection([('manual', 'Manually'), ('ramdomly', 'Randomly'), ('balanced', 'Balanced')],
                                     'Assign Method', required=True, default='manual')
    member_ids = fields.Many2many('res.users', string='Team Members')
    alias_id = fields.Many2one('mail.alias', string='Alias', ondelete="restrict",
                               help="The email address associated with this team. New emails received will automatically create new leads assigned to the team.")
    sequence = fields.Integer('Sequence', default=1, help="Used to order teams. Lower is better.")
    reply_to = fields.Char(string='Reply-To',
                           help="The email address put in the 'Reply-To' of all emails sent by Odoo about cases in this sales team")
    color = fields.Integer(string='Color Index', help="The color of the team")
    use_alias = fields.Boolean(string='Email alias')
    use_sla = fields.Boolean(string='SLA Policies')
    use_rating = fields.Boolean(string='Ratings')
    percentage_satisfaction = fields.Integer(string='% Happy')
    use_website_technical_inspection_rating = fields.Boolean(string='Website Rating')
    alias_domain = fields.Char(string='Alias domain')
    alias_name = fields.Char(string='Alias Name')

    def get_alias_model_name(self, vals):
        return 'technical_inspection.ticket'

    @api.model
    def create(self, values):
        values['alias_name'] = 'support'
        return super(Team, self.with_context(mail_create_nosubscribe=True)).create(values)

    # ----------------------------------------
    # technical_inspection Team Dashboard
    # ----------------------------------------

    @api.model
    def retrieve_dashboard(self):
        """" Fetch data to setup technical_inspection Dashboard """
        result = {
            'tickets': {
                'today': 0,
                'avg_open_hours': 0,
            },
            'high': {
                'today': 0,
                'avg_open_hours': 0,
            },
            'urgent': {
                'today': 0,
                'avg_open_hours': 0,
            },
            'closed': {
                'today': 0,
                'avg_seven_day': 0,
            },
            'show_demo': 0,
        }

        tickets = self.env['technical_inspection.ticket'].search([('user_id', '=', self._uid)])
        for ticket in tickets:
            # Expected closing
            if ticket.priority:
                if ticket.day_open > 0:
                    result['tickets']['avg_open_hours'] += 1
                if ticket.priority == 2 and ticket.day_open == 0:
                    result['high']['today'] += 1
                if ticket.priority == 2 and ticket.day_open > 0:
                    result['high']['avg_open_hours'] += 1
                if ticket.priority == 3 and ticket.day_open == 0:
                    result['urgent']['today'] += 1
                if ticket.priority == 3 and ticket.day_open > 0:
                    result['urgent']['avg_open_hours'] += 1
                if ticket.is_close and ticket.day_open == 0:
                    result['closed']['today'] += 1
                if ticket.is_close and 0 < ticket.day_open < 8:
                    result['closed']['avg_seven_day'] += 1


        result['tickets']['today'] = len(tickets)
        result['show_demo'] = True
        if len(tickets) > 0:
            result['show_demo'] = False

        result['rating_enable'] = True
        result['success_rate_enable'] = True
        return result