# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval

__all__ = ['Invoice']


class Invoice:
    __metaclass__ = PoolMeta
    __name__ = 'account.invoice'
    related_invoice = fields.Function(fields.Many2One('account.invoice',
            'Related Invoice', states={
                'invisible': Eval('invoice_type').in_(
                    ['out_invoice', 'in_invoice']),
                }, depends=['invoice_type']), 'get_related_invoice')

    @classmethod
    def get_related_invoice(cls, invoices, name):
        pool = Pool()
        InvoiceLine = pool.get('account.invoice.line')

        invoice_ids = [i.id for i in invoices]
        result = {}.fromkeys(invoice_ids, None)
        for invoice in invoices:
            if invoice.invoice_type in ('out_invoice', 'in_invoice'):
                continue
            for line in invoice.lines:
                if isinstance(line.origin, InvoiceLine):
                    result[invoice.id] = line.origin.invoice.id
                    break
        return result
