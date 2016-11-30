# -*- coding: utf-8 -*-
{
    'name': 'technical_inspection',
    'category': 'Inspecciones tecnicas para oportunidades',
    'version': '1.0',
    'description': """
technical_inspection Management.
====================

Like records and processing of claims, technical_inspection and Support are good tools
to trace your interventions. This menu is more adapted to oral communication,
which is not necessarily related to a claim. Select a customer, add notes
and categorize your interventions with a channel and a priority level.
    """,
    'author': 'Manexware S.A.',
    'website': 'http://www.manexware.com',
    'depends': ['mail','utm','mail'],
    'data': [
        # 'data/technical_inspection.team.csv',
        # 'data/technical_inspection.stage.csv',
        # 'data/technical_inspection.ticket.type.csv',
        # 'data/technical_inspection.tag.csv',
        # 'data/ticket_sequence.xml',
        'views/technical_inspection_templates.xml',
        'views/technical_inspection_menu.xml',
        'views/technical_inspection_tags_views.xml',
        'views/technical_inspection_ticket_type_views.xml',
        'views/technical_inspection_teams_views.xml',
        'views/technical_inspection_stages_views.xml',
        'views/technical_inspection_views.xml',
        # 'security/technical_inspection_security.xml',
        # 'security/ir.model.access.csv',
        # 'security/ir.rule.csv'
    ],
    'qweb': [
        "static/src/xml/technical_inspection_dashboard.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
