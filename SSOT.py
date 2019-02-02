from HSBCBusiness import HSBCBusiness
from GoCardless import GoCardless
from TransactionGatewayAbstract import TransactionGatewayAbstract
from TransactionGatewayAbstract import PartnerGatewayAbstract
import os, pickle

class SSOT(TransactionGatewayAbstract, PartnerGatewayAbstract):
    """ Single Source Of Truth (SSOT) transaction gateway.
    Merges other gateway transactions, and partner gateways
    """

    def __init__(self, target_gateways=None, date_from=None, refresh=False):
        self.target_gateways = target_gateways
        self.loaded_gateways = []
        self.transactions = []
        self.partners = []
        self.date_from = date_from
        self.refresh = refresh
        self.init()

    @staticmethod
    def get_name():
        return "Single Source of Truth"

    @staticmethod
    def get_short_name():
        return "SSOT"

    def init(self):
        if self.target_gateways is not None:
            for gateway in self.target_gateways:
                gatewayName = gateway['name']
                gatewayModule = __import__(gatewayName)
                gatewayClass = getattr(gatewayModule,gatewayName)
                shortName = gatewayClass.get_short_name()
                gatewayInstance = gatewayClass(gateway['construct'])

                if self.refresh: # Refresh SSOT
                    gatewayInstance.refreshTransactions(date_from=self.date_from)
                    #gatewayInstance.refreshPartners(self.date_from)
                else: # Perform initial SSOT fetch
                    gatewayInstance.fetchTransactions()
                    gatewayInstance.fetchPartners()
                    
                # Dynamically runs: from <gatewayName> import <gatewayClass>
                # and than adds <gatewayClass> instance as property to SSOT
                setattr(self, shortName, gatewayInstance)
                self.loaded_gateways.append(shortName)

        # Finally Join SSOT Partners & Transactions from all loaded gateways
        self.fetchTransactions()
        self.fetchPartners()

    def removeTransactionLog(self):
        here = os.path.dirname(__file__)                                         
        payments_file = os.path.join(here, 'payments.p')                      
        payouts_file = os.path.join(here, 'payouts.p')
        if os.path.isfile(payments_file):
            os.remove(payments_file)
        if os.path.isfile(payouts_file):
            os.remove(payouts_file)
        

    def fetchTransactions(self):
        # Load from pickle if there
        here = os.path.dirname(__file__)
        ssot_transactions_file = os.path.join(here, 'transactions.p')
        if os.path.isfile(ssot_transactions_file):
            self.transactions = pickle.load(open(ssot_transactions_file, 'rb'))
        else:
            if self.target_gateways is None:
                pass
            else:
                for gateway in self.loaded_gateways:
                    gatewayTransactions = self.__getattribute__(gateway).transactions
                    self.transactions = self.transactions + gatewayTransactions
            # Pickle it!
            pickle.dump(self.transactions, open(ssot_transactions_file, "wb"))

    def refreshTransactions(self):
        if self.target_gateways is None:
            pass
        else:
            for gateway in self.loaded_gateways:
                self.__getattribute__(gateway).refreshTransactions()
                gatewayTransactions = self.__getattribute__(gateway).transactions
                #TODO de-dupe when appending a refreshed list of transactions
                self.transactions = self.transactions + gatewayTransactions

    def fetchPartners(self):
        if self.target_gateways is None:
            pass
        else:
            for gateway in self.loaded_gateways:
                gatewayPartners = self.__getattribute__(gateway).partners
                self.partners = self.partners + gatewayPartners

    def refreshPartners(self):
        if self.target_gateways is None:
            pass
        else:
            self.partners = [] #Reset partners
            for gateway in self.loaded_gateways:
                gatewayPartners = self.__getattribute__(gateway).refreshPartners()
                self.partners = self.partners + gatewayPartners
        
    def filterby(self, source_gateway=None, source_id=None, reference=None, *args, **kwargs):
        if source_gateway:
            try:
                recordType = kwargs['recordType']
                if recordType is "Partner":
                    return filter(lambda x: source_gateway in x.source_gateway, self.partners)
            except KeyError:
                pass
            return filter(lambda x: source_gateway in x.source_gateway, self.transactions)
        if reference:
            return filter(lambda x: reference in x.reference, self.transactions)
	#Fallback return all
        return self.transactions

    def fuzzygroup(self):
        matches = {}
        for transaction in self.transactions:
             if transaction.reference in matches:
                 matches[transaction.reference].append(transaction)
             else:
                 matches[transaction.reference] = [transaction]
        return matches
