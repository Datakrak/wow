from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth
import os
import json
import pandas as pd

load_dotenv()
clientID = os.getenv('clientID')
clientSecret = os.getenv('clientSecret')
auth_str = f"{clientID}:{clientSecret}"
auth = HTTPBasicAuth(clientID, clientSecret)
#auth = base64.b64encode(auth_str.encode('ascii')).decode()


baseURL = "https://eu.api.blizzard.com"
namespace = 'dynamic-eu'


#Crée le Token pour accéder à l'API
def createAccessToken():
    data = {
        'grant_type': 'client_credentials'
    }

    res = requests.post("https://eu.battle.net/oauth/token", data=data, auth=auth)
    print(res)
    return res

#Retourne la liste des royaumes existants
def realmList():
    token = createAccessToken().json()
    access_token = token['access_token']
    realms_list = [('Id', 'nom')]

    url = f"{baseURL}/data/wow/connected-realm/index?namespace=dynamic-eu"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    res = json.loads(requests.get(url, headers=headers).content)
    
    #print(res["connected_realms"][0])

    for realms in res["connected_realms"]:
        res2 = json.loads(requests.get(realms["href"], headers=headers).content)
        for realm in res2["realms"]:
            try:
                realms_list.append((realm['id'], realm['name']['fr_FR']))
            except:
                print('Royaume non valable.')
                print(realm)

    df = pd.DataFrame(realms_list)
    df.to_csv("Liste_royaumes.csv", header=["id", "Nom"])
    


    



    return 0
    for realm in res["connected_realms"]:
        r = requests.get(realm["href"], headers=headers)
        print(r.content)

    
    #print(res.json())
    return 0


if __name__ == "__main__":
    realmList()
""" 
function createAccessToken() {
  var formData = {
    'grant_type': 'client_credentials'
  };

  var options = {
    'method': 'post',
    'payload': formData,
    'headers': {
      'Authorization': 'Basic ' + Utilities.base64Encode(ApiKey + ':' + ApiSecret)
    }
  };
  var url = 'https://' + region + '.battle.net/oauth/token';
  var response = UrlFetchApp.fetch(url, options);
  return JSON.parse(response.getContentText()).access_token;
}

function requeteAuctions(){
  var token = createAccessToken();

  var options = {
    'method': 'get',
    'headers': {
      'Authorization': 'Bearer ' + token
    }
  };

  var url = urlApi + "/data/wow/connected-realm/" + idServer + "/auctions?namespace=dynamic-eu";
  
  try{
    var response = UrlFetchApp.fetch(url, options);
  } catch(e){Logger.log(e)}
  
  var auctions = JSON.parse(response).auctions;
  Logger.log(auctions);
  return auctions;

} """