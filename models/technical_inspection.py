# -*- coding: utf-8 -*-

from odoo import api, fields, models

from odoo.tools.translate import _


class technical_inspectionTicket(models.Model):

    _name = "technical_inspection.ticket"
    _description = "technical_inspection Ticket"
    _order = "id desc"
    _inherit = ['mail.thread', 'ir.needaction_mixin', 'utm.mixin']
    _mail_mass_mailing = _('Issues / Support')

    def _default_probability(self):
        stage_id = self._default_stage_id()
        if stage_id:
            return self.env['technical_inspection.stage'].browse(stage_id).probability
        return 10

    def _default_stage_id(self):
        team = self.env['technical_inspection.team'].sudo()._get_default_team_id(user_id=self.env.uid)
        return self._stage_find(team_id=team.id, domain=[('fold', '=', False)]).id

    name = fields.Char('Subject', required=True)
    ticket_id = fields.Char(String='Ticket Id')
    technical_report_id = fields.Char('Technical Report Id')
    active = fields.Boolean('Active', default=True)
    create_date = fields.Datetime('Create Date', readonly=True)
    date_closed = fields.Datetime('Closed Date', readonly=True, copy=False)
    date_open = fields.Datetime('Assigned', readonly=True)
    team_id = fields.Many2one('technical_inspection.team', string='technical_inspection Team', oldname='section_id',
                              default=lambda self: self.env['technical_inspection.team'].sudo()._get_default_team_id(
                                  user_id=self.env.uid),
                               track_visibility='onchange',
                              help='When sending mails, the default email address is taken from the technical_inspection team.')
    kanban_state = fields.Selection(
        [('normal', 'Normal'), ('done', 'Ready for next step'), ('blocked', 'Blocked')],
        string='Activity State', default='normal',
        track_visibility='onchange',
        required=True, copy=False, compute='_compute_kanban_state')
    user_id = fields.Many2one('res.users', string='Responsible', index=True, track_visibility='onchange',
                              default=lambda self: self.env.user)
    priority = fields.Selection([('0', 'Low'), ('1', 'Normal'), ('2', 'High'), ('3', 'Urgent')], 'Priority', index=True, default='1')
    description = fields.Text('Description')
    partner_id = fields.Many2one('res.partner', 'Partner', index=True)
    partner_name = fields.Char("Customer Name", index=True)
    partner_email = fields.Char('Customer Email', help="Email address of the customer", index=True)
    ticket_type_id = fields.Many2one('technical_inspection.ticket.type', string='Ticket type')
    tag_ids = fields.Many2many('technical_inspection.tag', string='Tags')
    # stage_id = fields.Many2one('technical_inspection.stage', string='Stage', track_visibility='onchange', index=True,
    #                            domain="['|', ('team_ids', '=', False), ('team_ids', '=', team_id)]",
    #                            group_expand='_read_group_stage_ids', default=_default_stage_id)
    stage_id = fields.Many2one('technical_inspection.stage', string='Stage', track_visibility='onchange', index=True, default=1)
    day_open = fields.Float(compute='_compute_day_open', string='Days to Assign', store=True)
    day_close = fields.Float(compute='_compute_day_close', string='Days to Close', store=True)
    date_last_stage_update = fields.Datetime(string='Last Stage Update', index=True, default=fields.Datetime.now)
    partner_tickets = fields.Integer(string='partner tickets')
    resolved = fields.Text('Resolved')
    is_close = fields.Boolean('Closing Kanban stages', help='Tickets in this stages are considered as done.', readonly=True)
    assign_id = fields.Many2one('res.users',string='Assign')
    assign_date = fields.Datetime(string='Assign Date',readonly=True)
    user_ids = fields.Many2many('res.users',related='ticket_type_id.user_ids')


    @api.model
    def _onchange_stage_id_values(self, stage_id):
        """ returns the new values when stage_id has changed """
        if not stage_id:
            return {}
        stage = self.env['technical_inspection.stage'].browse(stage_id)
        return {'is_close': stage.is_close}

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        values = self._onchange_stage_id_values(self.stage_id.id)
        self.update(values)

    @api.multi
    def _compute_kanban_state(self):
        for ticket in self:
            kanban_state = 'normal'
            if ticket.user_id:
                kanban_state = 'done'
            ticket.kanban_state = kanban_state

    @api.multi
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        for record in self:
            if record.partner_id:
                record.partner_email = record.partner_id.email

    @api.depends('date_open')
    def _compute_day_open(self):
        """ Compute difference between create date and open date """
        for lead in self.filtered(lambda l: l.date_open):
            date_create = fields.Datetime.from_string(lead.create_date)
            date_open = fields.Datetime.from_string(lead.date_open)
            lead.day_open = abs((date_open - date_create).days)

    @api.depends('date_closed')
    def _compute_day_close(self):
        """ Compute difference between current date and log date """
        for lead in self.filtered(lambda l: l.date_closed):
            date_create = fields.Datetime.from_string(lead.create_date)
            date_close = fields.Datetime.from_string(lead.date_closed)
            lead.day_close = abs((date_close - date_create).days)

    # ----------------------------------------
    # ORM override (CRUD, fields_view_get, ...)
    # ----------------------------------------
    @api.model
    def create(self, vals):
        # set up sequencial
        code = self.env['ir.sequence'].next_by_code('technical_inspection.ticket')
        vals['ticket_id'] = "TK-%s" % code
        # set up context used to find the lead's sales team which is needed
        # to correctly set the default stage_id
        context = dict(self._context or {})
        if vals.get('ticket_type_id') and not self._context.get('default_type'):
            context['default_type'] = vals.get('ticket_type_id')
        if vals.get('team_id') and not self._context.get('default_team_id'):
            context['default_team_id'] = vals.get('team_id')

        if vals.get('user_id') and 'date_open' not in vals:
            vals['date_open'] = fields.Datetime.now()
        if vals.get('assign_id') and 'assign_date' not in vals:
            vals['assign_date'] = fields.Datetime.now()
        # context: no_log, because subtype already handle this
        return super(technical_inspectionTicket, self.with_context(context, mail_create_nolog=True)).create(vals)

    @api.multi
    def write(self, vals):
        # stage change: update date_last_stage_update
        if vals.get('assign_id') and 'assign_date' not in vals:
            vals['assign_date'] = fields.Datetime.now()
        if 'stage_id' in vals:
            vals['date_last_stage_update'] = fields.Datetime.now()
        if vals.get('user_id') and 'date_open' not in vals:
            vals['date_open'] = fields.Datetime.now()
        # stage change with new stage: update probability and date_closed
        if vals.get('stage_id'):
            vals.update(self._onchange_stage_id_values(vals.get('stage_id')))
        if vals.get('is_close'):
            vals['date_closed'] = fields.Datetime.now()
        else:
            vals['date_closed'] = False
        return super(technical_inspectionTicket, self).write(vals)

    # -------------------------------------------------------
    # Mail gateway
    # -------------------------------------------------------

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        self = self.with_context(default_user_id=False)

        if custom_values is None:
            custom_values = {}
        defaults = {
            'name': msg_dict.get('subject') or _("No Subject"),
            'email_from': msg_dict.get('from'),
            'email_cc': msg_dict.get('cc'),
            'partner_id': msg_dict.get('author_id', False),
        }
        if msg_dict.get('author_id'):
            defaults.update(self._onchange_partner_id_values(msg_dict.get('author_id')))
        defaults.update(custom_values)
        return super(technical_inspectionTicket, self).message_new(msg_dict, custom_values=defaults)

    # ----------------------------------------
    # Business Methods
    # ----------------------------------------

    def _stage_find(self, team_id=False, domain=None, order='sequence'):
        """ Determine the stage of the current lead with its teams, the given domain and the given team_id
            :param team_id
            :param domain : base search domain for stage
            :returns crm.stage recordset
        """
        # collect all team_ids by adding given one, and the ones related to the current leads
        team_ids = set()
        if team_id:
            team_ids.add(team_id)
        for ticket in self:
            if ticket.team_id:
                team_ids.add(ticket.team_id.id)
        # generate the domain
        if team_ids:
            search_domain = ['|', ('team_ids', '=', False), ('team_ids', 'in', list(team_ids))]
        else:
            search_domain = [('team_ids', '=', False)]
        # AND with the domain in parameter
        if domain:
            search_domain += list(domain)
        # perform search, return the first found
        return self.env['technical_inspection.stage'].search(search_domain, order=order, limit=1)

