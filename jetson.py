# This is the main controller running on Jetson TX1 board

from twisted.internet import reactor
from twisted.web.client import Agent
from twisted.web.http_headers import Headers

agent = Agent(reactor)
d = agent.request(
  b'GET',
  b'http://localhost:5000/hello',
  Headers({'User-Agent': ['HelloHello']}),
  None
)

def cbResponse(msg):
  print('Response received')

d.addCallback(cbResponse)

reactor.run()