import pandas as pd
import requests
import uuid
import json

CSV = "uterances.csv"
URL = "https://http.msging.net/commands"
KEY = "<BOT KEY>"

def get_payload(uterance="test"):
    
    payload = {"id": str(uuid.uuid1()),
               "to": "postmaster@ai.msging.net",
               "method": "set",
               "uri": "/analysis",
               "type": "application/vnd.iris.ai.analysis-request+json",
               "resource": {"text": uterance}}

    return payload

def main():

    df = pd.read_csv(CSV, sep=";")
    
    results = {'uterance': [],
               'intent': [],
               'predicted': [],
               'score': [],
               'flag': [],
               'log': []}

    for index, row in df.iterrows():
        uterance = str(row[0])
        intent   = str(row[1])

        headers = {'Authorization': KEY, 
                   'Content-Type': 'application/json'}
        payload = get_payload(uterance=uterance)

        try:
            r = requests.post(URL, headers=headers, data=json.dumps(payload))
            r.encoding= 'utf-8'

            if r.status_code != 200:
                raise Exception('HTTP Status: {}'.format(r.status_code))

            if not 'intentions' in r.json()['resource']:
                raise Exception('We have not intentions: {}'.format(r.json()))
            
            predict = r.json()['resource']['intentions'][0]
            
            flag = False
            if intent == predict['name']:
                flag = True
            
            results['uterance'].append(uterance)
            results['intent'].append(intent)
            results['predicted'].append(predict['name'])
            results['score'].append(round(predict['score'], 2))
            results['flag'].append(flag)
            results['log'].append(r.json()['resource']['intentions']) 

        except Exception as e:
            print("Error for {}: {}".format(uterance, e))
            continue

    df = pd.DataFrame.from_dict(results)
    df.to_excel("analysis.xlsx", sheet_name='uterance_predict', index=False) 

if __name__ == '__main__':
    main()