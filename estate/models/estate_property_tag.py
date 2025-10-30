from odoo import models, fields

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate Property Tag"
    _tag_uniq = models.Constraint(
        'unique (name)',
        'A property tag name must be unique',
    )
    _order = "name desc"

    name = fields.Char("Property Tag", required=True)
    color = fields.Integer('Color')