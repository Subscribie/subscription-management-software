from HSBCBusiness import HSBCBusiness
from GoCardless import GoCardless

class SSOT:
    """ Single Source Of Truth (SSOT) transaction gateway.
    Merges other gateway transactions
    """
    transactions = []

    def __init__(self):
        self.transactions = []
        self.init()

    def get_name(self):
        return "Single Source of Truth"

    def get_short_name(self):
        return "SSOT"

    def init(self):
        self.HSBC = HSBCBusiness()                                                            
        self.HSBC.fetchTransactions()                                                         
        self.GC = GoCardless()                                                                
        self.GC.fetchTransactions()

    def fetchTransactions(self):
        self.transactions = self.HSBC.transactions + self.GC.transactions

    def filterby(self, source_gateway=None, source_id=None, reference=None, *args, **kwargs):
        if source_gateway:
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
