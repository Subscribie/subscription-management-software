# -*- coding: utf-8 -*-
"""
    Subscriber Matching Service 
    ~~~~~
    Abstract interface for matching subscribers from arbitary payment 
    information providers, payment institutions, billing systems. 
    :copyright: © 2018 Karma Computing.
    :license: GPLv3, see LICENSE for more details.
"""
from __future__ import absolute_import
from abc import ABCMeta, abstractmethod
import os, gocardless_pro, json
import urllib2

class TransactionGatewayAbstract:
    __metaclass__ = ABCMeta

    def __init__(self):
        self.init()

    @abstractmethod
    def get_name(self):
        raise NotImplementedError()

    @abstractmethod
    def get_short_name(self):
        raise NotImplementedError()

    @abstractmethod
    def init(self):
        raise NotImplementedError()

    @abstractmethod
    def fetchTransactions(self):
        raise NotImplementedError()

class Stripe(TransactionGatewayAbstract):
    def get_name(self):
      return "Stripe"

class GoCardless(TransactionGatewayAbstract):
    def get_name(self):
      return "GoCardless"

    def get_short_name(self):
      return "GC"

    def init(self):
	self.gcclient = gocardless_pro.Client(
	    # We recommend storing your access token in an 
            # environment variable for security
	    access_token = os.getenv('gocardless'),
	    # Change this to 'live' when you are ready to go live.
	    environment = 'sandbox'
	)

    def fetchTransactions(self):
        pass

    def gc_get_payments(self):
        """Payment objects represent payments 
        from a customer to a creditor, taken against a Direct Debit mandate. 
        This method gets all the payments made to a merchant. WARNING remember
        a GoCardless `payment` means GoCardless has collected the money on your 
        behalf, a confirmed `payout` means you actuall have the money in your 
        account. With GoCardless, Payments are always made against a mandate 
        (a customer MAY have more than one mandate). 
        :meth:`gc_match_payments_to_payouts` matches payouts with payments by
        updating self.payments with the full payout meta data.
        :param None
        :return: list of payments
        """
        paymentList = self.gcclient.payments.list()
        records = paymentList.records
        after = paymentList.after
        while after is not None:
            fetchedPayments = self.gcclient.payments.list(params={"after":after,
                                                        "limit":500})
            after =  fetchedPayments.after
            records = records + fetchedPayments.records
        self.payments = records
        return records 

    def gc_get_payouts(self):
        """Payouts represent transfers from GoCardless to a creditor. 
        Each payout contains the funds collected from one or many payments. 
        Payouts are created automatically after a payment has been successfully 
        collected. These payouts are grouped, and paid to the merchant as
        payments (see gc_get_payments()) which are bundles of individual payouts, 
        which means they need to be unbundled to be made sense of.
        :param None
        :return: list of payouts
        """
        payoutList = self.gcclient.payouts.list()
        records = payoutList.records
        after = payoutList.after
        while after is not None:
            fetchedPayouts = self.gcclient.payouts.list(params={"after":after,
                                                        "limit":500})
            after =  fetchedPayouts.after
            records = records + fetchedPayouts.records
        self.payouts = records
        return records

    def gc_match_payments_to_payouts(self):
        """For each payment (if has been paid out), fetch the full  payout meta 
        data and replate the existing self.payments[index] payout ID with the 
        full payout meta data. 
        :return: None 
         """
        for paymentindex,payment in enumerate(self.payments):
            if 'payout' in payment.attributes['links']:
                payout_id = payment.attributes['links']['payout']
                # Update payment reference with full payout meta
                for payoutindex,payout in enumerate(self.payouts):
                    if self.payouts[payoutindex].id == payout_id:
                        payment.attributes['links']['payout'] = self.payouts[payoutindex]

    def gc_match_payments_to_mandate(self):
        """For each payment, update the links->mandate id reference with the 
        complete mandate data from GoCardless
        :return: None 
        """
        for paymentindex,payment in enumerate(self.payments):
	    mandate_id = payment.attributes['links']['mandate']
            mandate = self.gcclient.mandates.get(mandate_id)
            # Replace mandate id refernce with full mandate metadata
            self.payments[paymentindex].attributes['links']['mandate'] = mandate

    def gc_match_mandate_to_customer(self):
        """For each payment's mandate, update its 
        payment.attributes['links']['mandate'].attributes['links']['customer']
        reference with the complete customer meta data from GoCardless.
        :return: None 
        """
        for paymentindex,payment in enumerate(self.payments):
            customer_id = payment.attributes['links']['mandate'].attributes['links']['customer']
            customer = self.gcclient.customers.get(customer_id)
            self.payments[paymentindex].attributes['links']['mandate'].attributes['links']['customer'] = customer

if __name__ == "__main__":
    g = GoCardless()
    print "Getting all GoCardless payments"
    g.gc_get_payments()
    print "Getting all GoCardless payouts"
    g.gc_get_payouts()
    print "Matching payments to payouts"
    g.gc_match_payments_to_payouts()
    print "Matching payments to mandates"
    g.gc_match_payments_to_mandate()
    print "Matching mandate to customer" 
    g.gc_match_mandate_to_customer()

class Gamma(TransactionGatewayAbstract):
    def get_name(self):
      return "Gamma"



##############

## My ideal transaction object? ###

#{
#    'id': 'dsfd87487984423', # Controlled by us, possibly a hash of the dict?
#    'journal': {
#	'number': 'SAJ/2018/0197',
#        'reference': 'part refund for x',
#        'data': '07/10/2018',
#        'period': '07/2018',
#        'journal': 'Sales Journal (GBP)', 
#        'Customer': 'ACE Corp',
#        'Amount': 123,
#        'Currency': 'GBP', 
#	'Vatable'
#        
#    },
#}


##################
