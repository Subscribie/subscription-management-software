import os, pickle
import uuid
import time
import requests
from TransactionGatewayAbstract import PartnerGatewayAbstract
from TransactionGatewayAbstract import Partner

class HubSpot(PartnerGatewayAbstract):

    def __init__(self):
        self.partners = []
        try:
	    self.apikey = os.getenv('HUBSPOT_API_KEY')
	    if self.apikey is None:
		raise Exception()
        except Exception:
            print "HUBSPOT_API_KEY os environment var is not set"
            raise 


    def init(self):
        pass

    @staticmethod
    def get_name():
      return "HubSpot"

    @staticmethod
    def get_short_name():
      return "HUBSPOT"

    def fetchPartners(self):
        # Load from pickle if there
        if os.path.isfile('HUBSPOT_partners.p'):
            print "Unpickling all HubSport partners"
            self.HUBSPOT_partners = pickle.load(open('HUBSPOT_partners.p', 'rb'))
        else:
            print "Getting all HubSport partners"
            hubspot_partners = self.HUBSPOT_get_partners()
            # Pickle it!
            pickle.dump(self.HUBSPOT_partners, open("HUBSPOT_partners.p", "wb"))

        # Transform to generic Partner tuple
        for partner in self.HUBSPOT_partners:
            source_gateway = self.get_short_name()
            source_id = partner['canonical-vid']
            created_at = partner['identity-profiles'][0]['identities'][0]['timestamp']
            
            # Get email

            type = partner['identity-profiles'][0]['identities'][0]['type']
            isParimary = partner['identity-profiles'][0]['identities'][0]['is-primary']
            value = partner['identity-profiles'][0]['identities'][0]['value']
	    if type is 'EMAIL' and isParimary:
                email = value
            else:
                email = False

            given_name = partner['properties']['firstname']['value']
            family_name = partner['properties']['lastname']['value']

	    partnerRecord = Partner(uid=str(uuid.uuid4()),
			     created_at = created_at,                                   
			     source_gateway = self.get_short_name(),                  
			     source_id = source_id,                                    
			     billing_email = email,
			     given_name = given_name,                  
			     family_name = family_name,                                  
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

    def HUBSPOT_get_partners(self):
        """Partner objects represent partners
        :param None
        :return: list of partners
        """
        self.HUBSPOT_partners = []
	endpoint = 'https://api.hubapi.com/'                                                
	apikey = self.apikey
	resource = ''.join(['contacts/v1/lists/all/contacts/all?hapikey=', apikey,          
			    '&count=100'])                                                  
	url = ''.join([endpoint, resource])                                                 
											    
	response = requests.get(url).json()
        #Get & store first page
        self.HUBSPOT_partners = self.HUBSPOT_partners + response['contacts']

	numRequests = 0
        while response['has-more'] is True:
            numRequests = numRequests + 1
            if numRequests == 9:
                time.sleep(1)
                numRequests = 0
            self.HUBSPOT_partners = self.HUBSPOT_partners + response['contacts']
	    vid_offset = response['vid-offset']
            url = ''.join([endpoint, resource, '&vidOffset=', str(vid_offset)])

            response = requests.get(url)
            if response.status_code == 429:
                print "We got rate limitted" # TODO retry
            elif response.status_code == 200:
                response = response.json()
            print "Fetched " + `len(self.HUBSPOT_partners)` + " partners."

        # Fetch last page
	url = ''.join([endpoint, resource, '&vidOffset=', str(vid_offset)])
	response = requests.get(url)
	if response.status_code == 200:
	    response = response.json()
	    self.HUBSPOT_partners = self.HUBSPOT_partners + response['contacts']
	    print "Fetched last page " + `len(self.HUBSPOT_partners)` + " partners."
        

        return self.HUBSPOT_partners

h = HubSpot()
h.fetchPartners()
