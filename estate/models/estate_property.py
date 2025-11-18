from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"
    _check_expected_price = models.Constraint(
        'CHECK(expected_price > 0)',
        'A property expected price must be strictly positive'
    )
    _check_selling_price = models.Constraint(
        'CHECK(selling_price >= 0)',
        'A property selling price must be positive'
    )
    _order = "id desc"

    title = fields.Char(string="Title", required=True)
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postcode", size=5)
    date_availability = fields.Date(string="Available From", copy=False,
                                    default=fields.Date.today() + timedelta(days=90))
    expected_price = fields.Float(string="Expected Price", required=True)
    selling_price = fields.Float(string="Selling Price", readonly=True, copy=False)
    bedrooms = fields.Integer(string="Bedrooms", default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden Area (sqm)")
    garden_orientation = fields.Selection(
        string='Garden_Orientation',
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
    )
    state = fields.Selection(
        string='Status',
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('canceled', 'Canceled')
        ],
        default='new',
        compute='_compute_state',
        required=True,
        copy=False,
        readonly=True,
        store=True,
    )
    active = fields.Boolean(string="Active", default=True)

    property_type = fields.Many2one(
        comodel_name='estate.property.type',
        string='Property Type',
    )
    sales_person = fields.Many2one('res.users', string='Salesperson', index=True, default=lambda self: self.env.user)
    buyer = fields.Many2one('res.partner', string='Buyer', index=True, copy=False)
    tag_ids = fields.Many2many(comodel_name='estate.property.tag', string='Tags', column1="property_id",
                               column2="tag_id")
    offer_ids = fields.One2many(
        comodel_name='estate.property.offer',
        inverse_name='property_id',
        string='Offers',
    )

    @api.depends('offer_ids.status')
    def _compute_state(self):
        for record in self:
            # sold or canceled should not be overridden
            if record.state in ('sold', 'canceled'):
                continue

            accepted_offer = record.offer_ids.filtered(lambda o: o.status == 'accepted')
            if accepted_offer:
                record.state = 'offer_accepted'

    total_area = fields.Float(string="Total Area", compute="_compute_total_area")

    @api.constrains("selling_price")
    def _check_selling_price(self):
        for record in self:
            if record.selling_price < record.expected_price * 0.9:
                raise ValidationError("Selling price must be 90% of the expected price.")

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    best_price = fields.Float(string="Best Price", compute='_compute_best_price', store = True)

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            record.best_price = max(record.offer_ids.mapped("price"), default=0.0)

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "east"
        else:
            self.garden_area = 0
            self.garden_orientation = False

    def action_set_property_as_sold(self):
        # canceled property cannot be sold
        if self.state == 'canceled':
            raise UserError("Canceled property cannot be sold.")
        else:
            self.state = 'sold'

    def action_set_property_as_canceled(self):
        # sold property cannot be canceled
        if self.state == 'sold':
            raise UserError("Sold property cannot be canceled.")
        else:
            self.state = 'canceled'

    @api.ondelete(at_uninstall=False)
    def _unlink_except_new_or_canceled(self):
        if self.state != 'canceled' and self.state != 'new':
            raise UserError("Only new and canceled property can be deleted!")
