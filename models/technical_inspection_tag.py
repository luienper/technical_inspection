# -*- coding: utf-8 -*-

from odoo import fields, models

class Tag(models.Model):

    _name = "technical_inspection.tag"

    name = fields.Char('Name', required=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]
