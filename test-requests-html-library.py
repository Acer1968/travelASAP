
from requests_html import HTMLSession
session = HTMLSession()
r = session.get("https://www.travelasap.cz/chcete-jet-do/pensee-royal-garden/egypt/marsa-alam/19270a?sm=1#tab-terminy")
ele = r.html.find('#231208858', first=True)
print(ele)

r.html.render()
ele = r.html.find('#grid-box', first=True)
print(ele)
print(ele.attrs)
print(ele.html)
print(ele.absolute_links)
print(r.html)
print(r.html.search("231208858"))

