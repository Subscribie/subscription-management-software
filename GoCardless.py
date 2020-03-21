import os, pickle
import hashlib
from TransactionGatewayAbstract import TransactionGatewayAbstract
from TransactionGatewayAbstract import PartnerGatewayAbstract
from TransactionGatewayAbstract import Transaction, Partner
import gocardless_pro

class GoCardless(TransactionGatewayAbstract, PartnerGatewayAbstract):

    def __init__(self, construct):
        try:
            access_token = construct["access_token"]
        except KeyError:
            access_token = None

        try:
            environment = construct["environment"]
        except KeyError:
            environment = 'live'

        self.transactions = []
        self.partners = []
	    # We recommend storing your access token in an 
        # environment variable for security
        if access_token is None:
            access_token = os.getenv('gocardless')
        self.gcclient = gocardless_pro.Client(
            # Change this to 'live' when you are ready to go live.
            access_token,
            environment = environment
        )

    def init(self):
        pass

    @staticmethod
    def get_name():
      return "GoCardless"

    @staticmethod
    def get_short_name():
      return "GC"

    def fetchPartners(self, **kwargs):
        # Load from pickle if there, but only if kwargs refresh is false
        here = os.path.dirname(__file__)
        gc_partners_file = os.path.join(here, 'gc_partners.p')
        if os.path.isfile(gc_partners_file) and kwargs.pop('refresh', False) is False:
            gc_partners = pickle.load(open(gc_partners_file, 'rb'))
        else:
            print("Getting all GoCardless partners")
            gc_partners = self.gc_get_resources('customers')

            # Pickle it!
            pickle.dump(gc_partners, open(gc_partners_file, "wb"))

        # Transform to generic Partner tuple
        for partner in gc_partners:
            source_gateway = 'GC'
            source_id = partner.id

            # Set uid of Partner record as hash of its values
            m = hashlib.sha256()
            for attribute in partner.attributes:
              value = partner.__getattribute__(attribute)
              if value is not None:
                m.update(str(value).encode('utf-8'))
            uid = m.hexdigest()

            partnerRecord = Partner(uid=uid,
                 created_at = partner.created_at,                                   
                 source_gateway = self.get_short_name(),                  
                 source_id = partner.id,                                    
                 language = partner.language,
                 billing_email = partner.email,                    
                 given_name = partner.given_name,                  
                 family_name = partner.family_name,                                  
                 company_name = partner.company_name,                                 
                 billing_street = partner.address_line1,
                 billing_city = partner.city,                                 
                 billing_postal_code = partner.postal_code,                  
                 billing_country_code = partner.country_code,
                 shipping_street = partner.address_line1,
                 shipping_city = partner.city,
                 shipping_country_code = partner.country_code,
                 shipping_postal_code = partner.postal_code,
                 ) 

            if partnerRecord not in self.partners:
                self.partners.append(partnerRecord)

    def gc_get_resources(self, name=''):
        """Get all resource <name> from Gocardless api
        :param name: the name of the api resource to fetch
        :return: list of resources"""
        resourceList = self.gcclient.__getattribute__(name).list()
        records = resourceList.records
        after = resourceList.after
        while after is not None:
            fetchedRecords = self.gcclient.__getattribute__(name).list(params={"after":after,
                                                        "limit":500})
            after =  fetchedRecords.after
            records = records + fetchedRecords.records
        self.__setattr__(name, records)
        return records


    def fetchTransactions(self, **kwargs):
        # Load from pickle if there, but only if kwargs refresh is false
        here = os.path.dirname(__file__)
        gc_payments_file = os.path.join(here, 'payments.p')
        gc_payouts_file = os.path.join(here, 'payouts.p')

        if os.path.isfile(gc_payments_file) and os.path.isfile(gc_payouts_file) \
           and kwargs.pop('refresh', False) is False:
            self.payments = pickle.load(open(gc_payments_file, 'rb'))
            self.payouts = pickle.load(open(gc_payouts_file, 'rb'))
        else:
            print("Getting all GoCardless payments")
            self.gc_get_resources('payments')

            print("Getting all GoCardless payouts")
            self.gc_get_resources('payouts')

            print("Getting all mandates")
            self.gc_get_resources('mandates')

            print("Getting all customers")
            self.gc_get_resources('customers')

            print("Getting all subscriptions")
            self.gc_get_resources('subscriptions')

            print("Getting all creditors")
            self.gc_get_resources('creditors')

            print("Getting all creditor_bank_accounts")
            self.gc_get_resources('creditor_bank_accounts')

            print("Getting all customer_bank_accounts")
            self.gc_get_resources('customer_bank_accounts')

            print("Matching payments to payouts")
            self.gc_match_payments_to_payouts()
            print("Matching payments to mandates")
            self.gc_match_payments_to_mandate()
            print("Matching mandate to customers")
            self.gc_match_mandate_to_customer()
            print("Matching payments to subscriptions")
            self.gc_match_payments_to_subscription()
            print("Matching payments to creditors")
            self.gc_match_payments_to_creditors()
            print("Matching payouts to creditor bank accounts")
            self.gc_match_payouts_to_creditor_bank_account()
            print("Matching mandates to customer bank accounts")
            self.gc_match_mandate_to_customer_bank_account()

            # Pickle it!
            pickle.dump(self.payments, open(gc_payments_file, "wb"))
            pickle.dump(self.payouts, open(gc_payouts_file, "wb"))

        # Transform to generic Transaction tuple
        for transaction in self.payments:
            source_gateway = 'GC'
            source_id = transaction.id
            date = transaction.attributes['charge_date']
            amount = transaction.attributes['amount']
            reference = transaction.attributes['links']['mandate']['reference']
            description = transaction.attributes['description']
            created_at = transaction.attributes['created_at']
            currency = transaction.attributes['currency']
            mandate = transaction.attributes['links']['mandate']
            payout = transaction.attributes['links']['payout']
            charge_date = transaction.attributes['charge_date']
            creditor = transaction.attributes['links']['creditor']
            customer_bank_account = transaction.attributes['links']['mandate']['links']['customer_bank_account'] #TODO abstract
            customer = transaction.attributes['links']['mandate']['links']['customer']  #TODO abstract

            transaction = Transaction(source_gateway=source_gateway,
                                 source_id=source_id, date=date, amount=amount,
                                 reference=reference, description=description,
                                 created_at=created_at, currency=currency,
                                 mandate=mandate, payout=payout, 
                                 charge_date=charge_date)
            if transaction not in self.transactions:
                self.transactions.append(transaction)

    def gc_match_payouts_to_creditor_bank_account(self):
        """For each payout, update its
        payout.attributes['links']['creditor_bank_account'] reference with the 
        complete creditor meta data from GoCardless.
        :return: None 
        """
        for payoutindex,payout in enumerate(self.payouts):
            creditor_bank_account_id = payout.attributes['links']['creditor_bank_account']
            for creditor_bank_account in self.creditor_bank_accounts:
              if creditor_bank_account.id == creditor_bank_account_id:
                self.payouts[payoutindex].attributes['links']['creditor_bank_account'] = creditor_bank_account.attributes

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
                        self.payments[paymentindex].attributes['links']['payout'] = payout.attributes
            else:
                payment.attributes['links']['payout'] = None

    def gc_match_payments_to_mandate(self):
        """For each payment, update the links->mandate id reference with the 
        complete mandate data from GoCardless
        :return: None 
        """
        for paymentindex,payment in enumerate(self.payments):
            mandate_id = payment.attributes['links']['mandate']
            # Get mandate by id
            for mandate in self.mandates:
              if mandate.id == mandate_id:
                # Replace mandate id refernce with full mandate metadata
                self.payments[paymentindex].attributes['links']['mandate'] = mandate.attributes

    def gc_match_payments_to_subscription(self):
        """For each payment, (if a subscription exists) update the 
        links->subscription id reference with the complete mandate data from 
        GoCardless.
        :return: None 
        """
        for paymentindex,payment in enumerate(self.payments):
            if 'subscription' in payment.attributes['links']:
                subscription_id = payment.attributes['links']['subscription']
                for subscription in self.subscriptions:
                  if subscription.id == subscription_id:
                    # Update subsciption reference with full subscription meta
                    self.payments[paymentindex].attributes['links']['subscription'] = subscription.attributes

    def gc_match_mandate_to_customer(self):
        """For each payment's mandate, update its 
        payment.attributes['links']['mandate'].attributes['links']['customer']
        reference with the complete customer meta data from GoCardless.
        :return: None 
        """
        for paymentindex,payment in enumerate(self.payments):
            customer_id = payment.attributes['links']['mandate']['links']['customer']
            for customer in self.customers:
              if customer.id == customer_id:
                self.payments[paymentindex].attributes['links']['mandate']['links']['customer'] = customer.attributes

    def gc_match_mandate_to_customer_bank_account(self):
        """For each payment's mandate, update its
        payment.attributes['links']['mandate'].attributes['links']['customer_bank_account']
        reference with the complete customer bank account meta data from GoCardless.
        :return: None 
        """
        for paymentindex,payment in enumerate(self.payments):
            customer_bank_account_id = payment.attributes['links']['mandate']['links']['customer_bank_account']
            for customer_bank_account in self.customer_bank_accounts:
              if customer_bank_account.id == customer_bank_account_id:
                self.payments[paymentindex].attributes['links']['mandate']['links']['customer_bank_account'] = customer_bank_account.attributes

    def gc_match_payments_to_creditors(self):
        """For each payment, update its 
        payment.attributes['links']['creditor'] reference with the complete 
        creditor meta data from GoCardless.
        :return: None 
        """
        for paymentindex,payment in enumerate(self.payments):
            creditor_id = payment.attributes['links']['creditor']
            for creditor in self.creditors:
              if creditor.id == creditor_id:
                self.payments[paymentindex].attributes['links']['creditor'] = creditor.attributes
