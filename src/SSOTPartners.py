from TransactionGatewayAbstract import PartnerGatewayAbstract

class SSOTPartners(PartnerGatewayAbstract):                                      
    def __init__(self):                                                          
        self.init()                                                              

    @staticmethod                                                                                 
    def get_name():                                                          
        return "SSOT Partners"

    @staticmethod                                                                              
    def get_short_name():                                                    
        return "SSOTPartners"                                                    
                                                                                 
    def init(self):                                                              
        raise NotImplementedError()                                              
                                                                                 
    def fetchPartners(self):                                                     
        raise NotImplementedError()

