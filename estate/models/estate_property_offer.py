import datetime

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property offer"
    _check_offer_price = models.Constraint(
        'CHECK(price > 0)',
        'A property offer price must be strictly positive'
    )
    _order = "price desc"

    price = fields.Float(string="Price", digits=0, required=True)
    status = fields.Selection(
        selection=[('accepted', 'Accepted'), ('refused', 'Refused')], copy=False
    )

    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    property_id = fields.Many2one('estate.property', string='Property', required=True)
    date_deadline = fields.Date(string='Deadline', compute='_compute_date_deadline',
                                inverse='_inverse_date_deadline', store=True)
    validity = fields.Integer(string='Validity (Days)', default=7)

    @api.constrains('date_deadline')
    def _date_deadline(self):
        for record in self:
            if record.validity < 0:
                raise ValidationError("Invalid Date deadline or Validity, Deadline date cannot be in the past.")

    @api.depends("validity")
    def _compute_date_deadline(self):
        for record in self:
            record.date_deadline = fields.Date.today() + datetime.timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            record.validity = (record.date_deadline - fields.Date.today()).days

    @api.onchange('date_deadline')
    def _onchange_validity(self):
        for record in self:
            record.validity = (record.date_deadline - fields.Date.today()).days

    def action_accept_offer(self):
        for record in self:
            # Check if there is already an accepted offer for this property
            existing_accepted = self.env['estate.property.offer'].search([
                ('property_id', '=', record.property_id.id),
                ('status', '=', 'accepted')
            ], limit=1)

            if existing_accepted:
                raise UserError(
                    "An offer has already been accepted for this property."
                )

            record.status = 'accepted'
            record.property_id.selling_price = self.price
            record.property_id.buyer = self.partner_id

    def action_refuse_offer(self):
        for record in self:
            if record.status != 'refused':
                # TODO set selling price to 0
                # record.property_id.selling_price = 0
                record.status = 'refused'
