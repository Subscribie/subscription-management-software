from abc import ABCMeta, abstractmethod, abstractproperty
from collections import namedtuple

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

Transaction = namedtuple('Transaction', ['date', 'amount', 'reference',          
                                         'description', 'currency', 'mandate',   
                                         'payout', 'creditor', 'created_at',     
                                         'charge_date', 'customer_bank_account', 
                                         'customer', 'source_gateway',           
                                         'source_type', 'source_id'])            
                                                                                 
Transaction.__new__.__defaults__ = (None,) * len(Transaction._fields)
