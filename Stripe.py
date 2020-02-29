import hashlib
import os
import stripe
from TransactionGatewayAbstract import (
    PartnerGatewayAbstract,
    TransactionGatewayAbstract,
    Partner,
)


class Stripe(PartnerGatewayAbstract, TransactionGatewayAbstract):
    def __init__(self, access_token):
        self.partners = []
        self.transactions = []
        if access_token is None:
            access_token = os.getenv("stripe")
        stripe.api_key = access_token
        self.stripeclient = stripe

    @staticmethod
    def get_name():
        return "Stripe"

    @staticmethod
    def get_short_name():
        return "STRIPE"

    def fetchPartners(self, **kwargs):
        customers = self.stripeclient.Customer.list(limit=1000)

        for customer in customers:
            # Set uid of Partner record as hash of its values
            m = hashlib.sha256()
            m.update(customer.id.encode("utf-8"))
            m.update(customer["email"].encode("utf-8"))
            uid = m.hexdigest()

            partnerRecord = Partner(
                uid=uid,
                source_gateway=self.get_short_name(),
                billing_email=customer["email"],
            )

            if partnerRecord not in self.partners:
                self.partners.append(partnerRecord)

    def fetchTransactions(self, **kwargs):
        pass

