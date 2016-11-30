# -*- coding: utf-8 -*-

from odoo import fields, models

class Type(models.Model):

    _name = "technical_inspection.ticket.type"

    name = fields.Char('Name', required=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order types. Lower is better.")
    user_ids = fields.Many2many('res.users', string='Usuarios', ondelete='set null')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Type name already exists !"),
    ]
