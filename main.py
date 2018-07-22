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
        import pdb;pdb.set_trace()
	self.client = gocardless_pro.Client(
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
        from a customer to a creditor, taken against 
        a Direct Debit mandate.
        :param None
        :return: list of payments
        """
        paymentList = self.client.payments.list()
        records = paymentList.records
        after = paymentList.after
        while after is not None:
            fetchedPayments = self.client.payments.list(params={"after":after,
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
        payoutList = self.client.payouts.list()
        records = payoutList.records
        after = payoutList.after
        while after is not None:
            fetchedPayouts = self.client.payouts.list(params={"after":after,
                                                        "limit":500})
            after =  fetchedPayouts.after
            records = records + fetchedPayouts.records
        self.payouts = records
        return records

    def gc_match_payments_to_payouts(self, payments, payouts):
        """
        :param payments: list of GoCardless payment objects
        :param payouts: list of GoCardless payout objects
        :return: list of GoCardless payment objects with payout _embedded
         """
        # For each payment get its payout (if has happened)
        url = 'https://api-sandbox.gocardless.com/events?payout=PY123&action=paid'
        auth_token = ''.join(['Bearer ', os.getenv('gocardless')])
        headers = {'Authorization': auth_token,
                   'GoCardless-Version': '2015-07-06'}
        req = urllib2.Request(url, None, headers)
        try:
	    response = urllib2.urlopen(req)
	    the_page = json.loads(response.read())
            import pdb;pdb.set_trace()
        except urllib2.HTTPError as e:
            print e.code
            print e.read()
         


if __name__ == "__main__":
    g = GoCardless()
    g.gc_get_payments()
    g.gc_get_payouts()
    g.gc_match_payments_to_payouts(g.payments, g.payouts)

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
