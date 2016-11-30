# -*- coding: utf-8 -*-

from odoo import api, fields, models

AVAILABLE_PRIORITIES = [
    ('0', 'Normal'),
    ('1', 'Low'),
    ('2', 'High'),
    ('3', 'Very High'),
]


class Stage(models.Model):
    _name = "technical_inspection.stage"
    _description = "Stage of case"
    _rec_name = 'name'
    _order = "sequence, name, id"

    @api.model
    def default_get(self, fields):
        ctx = dict(self.env.context)
        if ctx.get('default_team_id') and not ctx.get('technical_inspection_team_mono'):
            ctx.pop('default_team_id')
        return super(Stage, self.with_context(ctx)).default_get(fields)

    name = fields.Char('Stage Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    team_ids = fields.Many2many('technical_inspection.team', string='Team', ondelete='set null',
                              help='Specific team that uses this stage. '
                                   'Other teams will not be able to see or use this stage.')
    is_close = fields.Boolean('Closing Kanban stages', help='Tickets in this stages are considered as done.')
    fold = fields.Boolean('Folded',
                          help='This stage is folded in the kanban view '
                               'when there are no records in that stage to display.')