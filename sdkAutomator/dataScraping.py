# import requests
# from bs4 import BeautifulSoup

# class dataScraping(object):
#     def __init__(self, ele):
#         self.ele = ele
#         if self.ele == 'certificates_server':
#             self.replaced_ele = self.ele.replace('certificates_server', '/certificates/servers')
#         elif self.ele == 'volumes':
#             self.replaced_ele = self.ele.replace('volumes', 'storage-volumes')
#         else:
#             self.replaced_ele = self.ele.replace('_', '-')

#     def data_scraped(self):
#         """
#         Scrapping data for list of endpoints from API docs.
#         """
#         URL = "https://techlibrary.hpe.com/docs/enterprise/servers/oneview5.3/cicf-api/en/rest/" + self.replaced_ele + ".html.js"
#         r = requests.get(URL)

#         soup = BeautifulSoup(r.content, 'html5lib')  # If this line causes an error, run 'pip install html5lib' or install html5lib
#         body = soup.find('body')
#         string = str(body).replace('<body>define([],"', '').replace('");</body>', '')
#         soup = BeautifulSoup(string, 'html5lib')
#         api_list = soup.find('div', {"class": "\\\"api-list\\\""})
#         api_with_method = []
#         http_methods = []
#         apis = []
#         for span in api_list.find_all('span', {'class', '\\\"uri\\\"'}):
#             apis.append(span.text.strip())
#         for span in api_list.find_all('span', {'class', '\\\"method'}):
#             http_methods.append(span.text.strip())
#         for http_method, api in zip(http_methods, apis):
#             api_with_method.append({api, http_method})
        
#         return api_with_method