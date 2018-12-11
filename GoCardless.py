import os, pickle
import uuid
from TransactionGatewayAbstract import TransactionGatewayAbstract
from TransactionGatewayAbstract import PartnerGatewayAbstract
from TransactionGatewayAbstract import Transaction, Partner
import gocardless_pro

class GoCardless(TransactionGatewayAbstract, PartnerGatewayAbstract):

    def __init__(self, access_token=None):
        self.transactions = []
        self.partners = []
	    # We recommend storing your access token in an 
        # environment variable for security
        if access_token is None:
            access_token = os.getenv('gocardless')
	self.gcclient = gocardless_pro.Client(
	    # Change this to 'live' when you are ready to go live.
        access_token,
	    environment = 'live'
	)

    def init(self):
        pass

    @staticmethod
    def get_name():
      return "GoCardless"

    @staticmethod
    def get_short_name():
      return "GC"

    def fetchPartners(self):
        # Load from pickle if there
        here = os.path.dirname(__file__)
        gc_partners_file = os.path.join(here, 'gc_partners.p')
        if os.path.isfile(gc_partners_file):
            gc_partners = pickle.load(open(gc_partners_file, 'rb'))
        else:
            print "Getting all GoCardless partners"
            gc_partners = self.gc_get_partners()

            # Pickle it!
            pickle.dump(gc_partners, open(gc_partners_file, "wb"))

        # Transform to generic Partner tuple
        for partner in gc_partners:
            source_gateway = 'GC'
            source_id = partner.id

	    partnerRecord = Partner(uid=str(uuid.uuid4()),
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

    def gc_get_partners(self):
        """Partner objects represent partners
        :param None
        :return: list of partners
        """
        partnerList = self.gcclient.customers.list()
        records = partnerList.records
        after = partnerList.after
        while after is not None:
            fetchedPartners = self.gcclient.customers.list(params={"after":after,
                                                        "limit":500})
            after =  fetchedPartners.after
            records = records + fetchedPartners.records
        return records 


    def fetchTransactions(self):
        # Load from pickle if there
        here = os.path.dirname(__file__)
        gc_payments_file = os.path.join(here, 'payments.p')
        gc_payouts_file = os.path.join(here, 'payouts.p')

        if os.path.isfile(gc_payments_file) and os.path.isfile(gc_payouts_file):
            self.payments = pickle.load(open(gc_payments_file, 'rb'))
            self.payouts = pickle.load(open(gc_payouts_file, 'rb'))
        else:
            print "Getting all GoCardless payments"
            self.gc_get_payments()
            print "Getting all GoCardless payouts"
            self.gc_get_payouts()
            print "Matching payments to payouts"
            self.gc_match_payments_to_payouts()
            print "Matching payments to mandates"
            self.gc_match_payments_to_mandate()
            print "Matching mandate to customers" 
            self.gc_match_mandate_to_customer()
            print "Matching payments to subscriptions"
            self.gc_match_payments_to_subscription()
            print "Matching payments to creditors"
            self.gc_match_payments_to_creditors()
            print "Matching payouts to creditor bank accounts"
            self.gc_match_payouts_to_creditor_bank_account()
            print "Matching mandates to customer bank accounts"
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
            charge_date = transaction.attributes['charge_date']
            creditor = transaction.attributes['links']['creditor']
            customer_bank_account = transaction.attributes['links']['mandate']['links']['customer_bank_account'] #TODO abstract
            customer = transaction.attributes['links']['mandate']['links']['customer']  #TODO abstract

            transaction = Transaction(source_gateway=source_gateway,
                                 source_id=source_id, date=date, amount=amount,
                                 reference=reference, description=description,
                                 created_at=created_at, currency=currency,
                                 mandate=mandate, charge_date=charge_date)
            if transaction not in self.transactions:
                self.transactions.append(transaction)

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

    def gc_match_payouts_to_creditor_bank_account(self):
        """For each payout, update its
        payout.attributes['links']['creditor_bank_account'] reference with the 
        complete creditor meta data from GoCardless.
        :return: None 
        """
        for payoutindex,payout in enumerate(self.payouts):
            creditor_bank_account_id = payout.attributes['links']['creditor_bank_account']
            creditor_bank_account = self.gcclient.creditor_bank_accounts.get(creditor_bank_account_id)
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
                        payment.attributes['links']['payout'] = self.payouts[payoutindex].attributes

    def gc_match_payments_to_mandate(self):
        """For each payment, update the links->mandate id reference with the 
        complete mandate data from GoCardless
        :return: None 
        """
        for paymentindex,payment in enumerate(self.payments):
	    mandate_id = payment.attributes['links']['mandate']
            mandate = self.gcclient.mandates.get(mandate_id)
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
                subscription = self.gcclient.subscriptions.get(subscription_id)
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
            customer = self.gcclient.customers.get(customer_id)
            self.payments[paymentindex].attributes['links']['mandate']['links']['customer'] = customer.attributes

    def gc_match_mandate_to_customer_bank_account(self):
        """For each payment's mandate, update its
        payment.attributes['links']['mandate'].attributes['links']['customer_bank_account']
        reference with the complete customer bank account meta data from GoCardless.
        :return: None 
        """
        for paymentindex,payment in enumerate(self.payments):
            customer_bank_account_id = payment.attributes['links']['mandate']['links']['customer_bank_account']
            customer_bank_account = self.gcclient.customer_bank_accounts.get(customer_bank_account_id)
            self.payments[paymentindex].attributes['links']['mandate']['links']['customer_bank_account'] = customer_bank_account.attributes

    def gc_match_payments_to_creditors(self):
        """For each payment, update its 
        payment.attributes['links']['creditor'] reference with the complete 
        creditor meta data from GoCardless.
        :return: None 
        """
        for paymentindex,payment in enumerate(self.payments):
            creditor_id = payment.attributes['links']['creditor']
            creditor = self.gcclient.creditors.get(creditor_id)
            self.payments[paymentindex].attributes['links']['creditor'] = creditor.attributes

