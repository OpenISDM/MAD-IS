import requests


topic_dictionary = {
        'json'  : './facility.json',
        'rdf'  : './ex4.rdf',
        'wgsi' : './app.wsgi'
}
#headers = {'Content-Type': 'multipart/form-data',
#           'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'
#           }

for x in topic_dictionary:
    files = {'file': open(topic_dictionary[x], 'rb')}
    print files['file'].read()
    r = requests.post("http://140.109.22.142/callback", files=files)
    print r.text
