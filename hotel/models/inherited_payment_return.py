# Copyright 2017  Dario Lodeiros
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields, api, _


class PaymentReturn(models.Model):
    _inherit = 'payment.return'

    # Fields declaration
    folio_id = fields.Many2one(
        'hotel.folio',
        string='Folio')
    hotel_id = fields.Many2one(
        'hotel.property',
        store=True,
        readonly=True,
        related='folio_id.hotel_id')

    # Business methods
    @api.multi
    def action_confirm(self):
        pay = super(PaymentReturn, self).action_confirm()
        if pay:
            folio_ids = []
            folios = self.env['hotel.folio'].browse(folio_ids)
            for line in self.line_ids:
                payments = self.env['account.payment'].search([
                    ('move_line_ids', 'in', line.move_line_ids.ids)
                ])
                folios_line = self.env['hotel.folio'].browse(payments.mapped('folio_id.id'))
                for folio in folios_line:
                    if self.id not in folio.return_ids.ids:
                        folio.update({'return_ids': [(4, self.id)]})
                    msg = _("Return of %s registered") % (line.amount)
                    folio.message_post(subject=_('Payment Return'), body=msg)
                folios += folios_line
            folios.compute_amount()
