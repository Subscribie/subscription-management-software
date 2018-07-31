# -*- coding: utf-8 -*-
"""
    Subscriber Matching Service 
    ~~~~~
    Abstract interface for matching subscribers from arbitary payment 
    information providers, payment institutions, billing systems. 
    :copyright: © 2018 Karma Computing.
    :license: GPLv3, see LICENSE for more details.
"""


'''
 How to decide if a partner is already matched in matched_source_gateways.
 We use the word 'partner' instead of 'customer' to normalise these types of
 records, inspired by Odoo's data model, whereas Salesforce uses the word
 'account' for the same purpose.

 1) Take a customer object from a TransactionGatewayAbstract
 2) Extract the unique id which the TransactionGateway provides for the partner 
 3) Generate a look-up id (aka TransactionGatewayPartnerId) by concatenating the 
    TransactionGatewayAbstract.get_short_name with the unique partner id
    provided by the TransactionGateway being inspected. (We loosely take
    inspiration from MAC Organisationally Unique Identifier (OUI) concept to
    ensure uniqueness.
 4) Query the Partner object for the computed TransactionGatewayPartnerId
 5) If the TransactionGatewayPartnerId exists within a Partner's 
    matched_source_gateways attribute, then this record corresponds to that
    gateway. If not, then this is considered a new 'unseen' Partner records
    which MAY have data which can be used to update the Partner record.
'''


from SSOT import SSOT
from HSBCBusiness import HSBCBusiness
from GoCardless import GoCardless
from Gamma import Gamma

from webapp import app

if __name__ == "__main__":
    GC = GoCardless()
    GC.fetchPartners()
    pass

