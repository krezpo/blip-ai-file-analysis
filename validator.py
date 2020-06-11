import pandas as pd
import numpy as np
import requests
import uuid
import json

from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score

CSV = "utterances.csv"
URL = "https://http.msging.net/commands"
KEY = YOUR BOT KEY

def get_payload(utterance="test"):
    
    payload = {"id": str(uuid.uuid1()),
               "to": "postmaster@ai.msging.net",
               "method": "set",
               "uri": "/analysis",
               "type": "application/vnd.iris.ai.analysis-request+json",
               "resource": {"text": utterance}}

    return payload

def get_metrics(score, flag, intent, predicted):

    metrics = {'Item': ['Total',
                        'Classificados Corretamente',
                        'Classificados Incorretamente',
                        'Confiabilidade Média',
                        'Acurácia',
                        'Precisão',
                        'Recall',
                        'F1 Score'],

               'Valor': [len(score),
                         flag.count(True),
                         flag.count(False),
                         round(np.mean(score), 2),
                         round(accuracy_score(intent, predicted), 2),
                         round(precision_score(intent, predicted, average='micro'), 2),
                         round(recall_score(intent, predicted, average='micro'), 2),
                         round(f1_score(intent, predicted, average='micro'), 2)]}

    return metrics

def main():

    df = pd.read_csv(CSV, sep=";")
    
    results = {'utterance': [],
               'intent': [],
               'predicted': [],
               'score': [],
               'flag': [],
               'log': []}

    for index, row in df.iterrows():
        utterance = str(row[0])
        intent    = str(row[1])

        headers = {'Authorization': KEY, 
                   'Content-Type': 'application/json'}
        payload = get_payload(utterance=utterance)

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
            
            results['utterance'].append(utterance)
            results['intent'].append(intent)
            results['predicted'].append(predict['name'])
            results['score'].append(round(predict['score'], 2))
            results['flag'].append(flag)
            results['log'].append(r.json()['resource']['intentions']) 

        except Exception as e:
            print("Error for {}: {}".format(utterance, e))
            continue

    metrics = get_metrics(score=results['score'], 
                          flag=results['flag'], 
                          intent=results['intent'], 
                          predicted=results['predicted'])

    writer = pd.ExcelWriter('analysis.xlsx')
    df = pd.DataFrame.from_dict(results)
    df.to_excel(writer, sheet_name='utterance_predict', index=False) 
    df = pd.DataFrame.from_dict(metrics)
    df.to_excel(writer, sheet_name='metrics', index=False) 

    writer.save()

    print("Done")

if __name__ == '__main__':
    main()