# -*- coding: utf-8 -*-
"""
    Subscriber Matching Service 
    ~~~~~
    Abstract interface for matching subscribers from arbitary payment 
    information providers, payment institutions, billing systems. 
    :copyright: © 2018 Karma Computing.
    :license: GPLv3, see LICENSE for more details.
"""

from SSOT import SSOT
from HSBCBusiness import HSBCBusiness
from GoCardless import GoCardless
from Gamma import Gamma

from webapp import app

if __name__ == "__main__":
    HSBC = HSBCBusiness()
    HSBC.fetchPartners()
    HSBC.fetchTransactions()
    GC = GoCardless()
    GC.fetchPartners()
    SSOT = SSOT()
    SSOT.fetchTransactions()
    SSOT.fetchPartners()