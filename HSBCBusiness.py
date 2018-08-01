import os, datetime
import csv, hashlib, uuid
from TransactionGatewayAbstract import TransactionGatewayAbstract, Transaction
from TransactionGatewayAbstract import PartnerGatewayAbstract, Partner

class HSBCBusiness(TransactionGatewayAbstract, PartnerGatewayAbstract):
    """ The supported HSBC export is csv. The csv header is:
    'Date    Type    Description Paid out    Paid in Balance'
    Date format is: %d %b %Y  e.g. 12 Mar 2018
    """

    def __init__(self):
        self.transactions = []
        self.partners = []

    def get_name(self):
        return "HSBC Business"

    def get_short_name(self):
        return "HSBCB"

    def init(self):
        pass

    def fetchTransactions(self):
        self.hsbc_combine_exports()
        pass

    def hsbc_combine_exports(self):
        """Get all transaction export csv files, concatenate them and 
        read into self.transactions
        :param None
        :return: list of payments
        """
        self.hsbc_transactions = []

        for root, dirs, statement_exports in os.walk('./exports/hsbc'):
            pass

        for statement_export in statement_exports: 
            with open(''.join(['./exports/hsbc/', statement_export]), 'rb') as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar='"')
                header = next(reader) # Take header
                for row in reader:
                    date = row.pop(0)
                    row.insert(0, datetime.datetime.strptime(date, "%d %b %Y").date())
                    self.hsbc_transactions.append(row)
                    # Transform to generic Transaction tuple
                    if len(row[3]) is not 1:
                        amount = ''.join(['-',row[3]]) #HSBC payout
                    if len(row[4]) is not 1: #HSBC payment inward
                        amount = row[4]
		    transaction = Transaction(source_gateway='HSBCB',
                                             source_id=row[2],source_type=row[1],
                                             date=row[0], amount=amount, 
                                             reference=row[2], currency='GBP')
		    if transaction not in self.transactions:
		        self.transactions.append(transaction)
    def fetchPartners(self):
        hsbc_partners = self.hsbc_fetch_partners()

    def hsbc_fetch_partners(self):
        """Get all transaction export csv files, concatenate them and then
        extract information relevant to a Partner record.
        Read records into self.partners
        :param None
        :return: list of partners
        """
        self.hsbc_partners = []

        for root, dirs, statement_exports in os.walk('./exports/hsbc'):
            pass

        for statement_export in statement_exports: 
            with open(''.join(['./exports/hsbc/', statement_export]), 'rb') as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar='"')
                header = next(reader) # Take header
                for row in reader:
                    date = row.pop(0)
                    row.insert(0, datetime.datetime.strptime(date, "%d %b %Y").date())
                    self.hsbc_partners.append(row)
                    # Transform to generic Partner tuple
                    if len(row[3]) is not 1:
                        amount = ''.join(['-',row[3]]) #HSBC payout
                    if len(row[4]) is not 1: #HSBC payment inward
                        amount = row[4]
                    source_id = hashlib.sha512(str(row)).digest()
                    source_type = row[1]
                    company_name = row[2]
		    partner = Partner(uid = str(uuid.uuid4()),                                          
				     created_at = date,
				     source_gateway = self.get_short_name(),
				     source_id = source_id,                                    
				     source_type = source_type,                                  
				     company_name = company_name,                                 
				     ) 
		    if partner not in self.partners:
		        self.partners.append(partner)
