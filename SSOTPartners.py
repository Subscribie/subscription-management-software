from TransactionGatewayAbstract import PartnerGatewayAbstract

class SSOTPartners(PartnerGatewayAbstract):                                      
    def __init__(self):                                                          
        self.init()                                                              
                                                                                 
    def get_name(self):                                                          
        return "SSOT Partners"                                                   
                                                                                 
    def get_short_name(self):                                                    
        return "SSOTPartners"                                                    
                                                                                 
    def init(self):                                                              
        raise NotImplementedError()                                              
                                                                                 
    def fetchPartners(self):                                                     
        raise NotImplementedError()

