from HSBCBusiness import HSBCBusiness
from GoCardless import GoCardless
from TransactionGatewayAbstract import TransactionGatewayAbstract
from TransactionGatewayAbstract import PartnerGatewayAbstract

class SSOT(TransactionGatewayAbstract, PartnerGatewayAbstract):
    """ Single Source Of Truth (SSOT) transaction gateway.
    Merges other gateway transactions, and partner gateways
    """

    def __init__(self, target_gateways=None):
        self.target_gateways = target_gateways
        self.loaded_gateways = []
        self.transactions = []
        self.partners = []
        self.init()

    @staticmethod
    def get_name():
        return "Single Source of Truth"

    @staticmethod
    def get_short_name():
        return "SSOT"

    def init(self):
        if self.target_gateways is None:
            self.HSBC = HSBCBusiness()
            self.HSBC.fetchTransactions()
            self.HSBC.fetchPartners()
            self.loaded_gateways.append('HSBC')
            self.GC = GoCardless()
            self.GC.fetchTransactions()
            self.GC.fetchPartners()
            self.loaded_gateways.append('GC')
        else:
            for gateway in self.target_gateways:
                gatewayName = gateway['name']
                gatewayModule = __import__(gatewayName)
                gatewayClass = getattr(gatewayModule,gatewayName)
                shortName = gatewayClass.get_short_name()
                gatewayInstance = gatewayClass(gateway['construct'])
                gatewayInstance.fetchTransactions()
                gatewayInstance.fetchPartners()
                # Dynamically runs: from <gatewayName> import <gatewayClass>
                # and than adds <gatewayClass> instance as property to SSOT
                setattr(self, shortName, gatewayInstance)
                self.loaded_gateways.append(shortName)

        # Finally Join SSOT Partners & Transactions from all loaded gateways
        self.fetchTransactions()
        self.fetchPartners()

    def fetchTransactions(self):
        if self.target_gateways is None:
            self.transactions = self.HSBC.transactions + self.GC.transactions
        else:
            for gateway in self.loaded_gateways:
                gatewayTransactions = self.__getattribute__(gateway).transactions
                self.transactions = self.transactions + gatewayTransactions

    def fetchPartners(self):
        if self.target_gateways is None:
            self.partners = self.HSBC.partners + self.GC.partners
        else:
            for gateway in self.loaded_gateways:
                gatewayPartners = self.__getattribute__(gateway).partners
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
