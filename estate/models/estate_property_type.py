from odoo import models, fields

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Type"
    _type_uniq = models.Constraint(
        'unique (name)',
        'A property type name must be unique',
    )
    _order = "sequence, name"
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    name = fields.Char("Property Type", required=True)
    # TODO
    property_ids = fields.One2many("estate.property", inverse_name="property_type", string="Property Types", readonly=True)