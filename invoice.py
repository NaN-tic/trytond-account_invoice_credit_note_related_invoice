# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction

__all__ = ['Invoice', 'CreditInvoice']


class Invoice:
    __metaclass__ = PoolMeta
    __name__ = 'account.invoice'
    related_invoice = fields.Function(
        fields.Many2One('account.invoice', 'Related Invoice'),
        'get_related_invoice')

    @classmethod
    def get_related_invoice(cls, invoices, name):
        pool = Pool()
        InvoiceLine = pool.get('account.invoice.line')

        invoice_ids = [i.id for i in invoices]
        result = {}.fromkeys(invoice_ids, None)
        for invoice in invoices:
            if '_invoice' in invoice.invoice_type_criteria():
                continue
            for line in invoice.lines:
                if isinstance(line.origin, InvoiceLine):
                    result[invoice.id] = line.origin.invoice.id
                    break
        return result


class CreditInvoice:
    __metaclass__ = PoolMeta
    __name__ = 'account.invoice.credit'

    @classmethod
    def __setup__(cls):
        super(CreditInvoice, cls).__setup__()
        cls._error_messages.update({
                'invoice_non_posted': ('You can not credit '
                'invoice "%s" because it is not posted.'),
                })

    def do_credit(self, action):
        pool = Pool()
        Invoice = pool.get('account.invoice')

        invoices = Invoice.browse(Transaction().context['active_ids'])
        for invoice in invoices:
            if invoice.state not in ('posted', 'paid'):
                self.raise_user_error('invoice_non_posted',
                    (invoice.rec_name,))
        return super(CreditInvoice, self).do_credit(action)
