import os, pickle
import hashlib
from TransactionGatewayAbstract import TransactionGatewayAbstract
from TransactionGatewayAbstract import PartnerGatewayAbstract
from TransactionGatewayAbstract import Transaction, Partner
import gocardless_pro

access_token = os.getenv('gocardless')
self.gcclient = gocardless_pro.Client(
    # Change this to 'live' when you are ready to go live.
    access_token,
    environment = 'live'
)

def fetchPartners(self, **kwargs):
  """
  1) Get latest partner from Kafka topic, use as the `after` option in
      GoCarldess cursor pagination (https://developer.gocardless.com/api-reference/#api-usage-cursor-pagination)
  2) Start consumer to consumer any entries `after` that point
  3) Place them into the topic
  """

def kafka_get_gc_latest_partner_id()
  """Get the latest GoCardless partner ID we've stored in kafka and return it"""
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

        ######## Post to Kafka (don't do here, just testing)
        from aiokafka import AIOKafkaProducer
        import asyncio
        import json

        def serializer(value):
          return json.dumps(value).encode()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def send_one():
            producer = AIOKafkaProducer(
                loop=loop, bootstrap_servers='localhost:9092',
                value_serializer=serializer,
                compression_type="gzip",
                enable_idempotence=True)
            # Get cluster layout and initial topic/partition leadership information
            await producer.start()
            try:
                # Produce message
                await producer.send_and_wait("karmabroadband-partners", partnerRecord)
            finally:
                # Wait for all pending messages to be delivered or expire.
                await producer.stop()

        loop.run_until_complete(send_one())
                               
        ########################
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
