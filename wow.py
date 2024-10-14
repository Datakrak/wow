from dotenv import load_dotenv
from datetime import datetime
import requests
import os
import json
import pandas as pd
from models import Base, Item, Auction
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


load_dotenv()
#Authentification de l'application Blizzard pour accès API wow.
clientID = os.getenv('clientID')
clientSecret = os.getenv('clientSecret')
auth = (clientID, clientSecret)

#Coordonnées de la BDD pour lecture et écriture des données. 
DB_IP=os.getenv('DB_IP')
DB_USER=os.getenv('DB_USER')
DB_PWD=os.getenv('DB_PWD')
DB_NAME=os.getenv('DB_NAME')

db_url = f"mysql+pymysql://{DB_USER}:{DB_PWD}@{DB_IP}:3306/{DB_NAME}"

engine = create_engine(db_url)

#Autres variables globales
realm_kt = 512 #Identifiant du royaume de Kael'Thas

baseURL = "https://eu.api.blizzard.com"
namespace = 'static-eu' #A définir par requête, ne peut pas être toujours la même valeur.


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
    
#Récupère les données de toutes les auctions de WoW.
def auctions():
    token = createAccessToken().json()
    access_token = token['access_token']
    url = f"{baseURL}/data/wow/auctions/commodities?namespace=dynamic-eu"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    stamp = f"{hour}-{day}-{month}-{year}"

    print("Current Time =", current_time)

    try:
        res = json.loads(requests.get(url, headers=headers).content)
    except:
        print("Echec dans l'établissement de la connection. Fonction auctions.")


    for auction in res["auctions"]:

        
        auction_data = {
            "ID": f"{stamp}-{auction['id']}",
            "ID_AUCTION": auction['id'],
            "ID_ITEM": auction['item']['id'],
            "PRICE":auction['unit_price'],
            "QUANTITY": auction['quantity'],
            "TIME_LEFT": auction['time_left']
        }
        Session = sessionmaker(bind=engine)
        session = Session()

        if not verify_item(auction_data["ID_ITEM"]):
            item_data = item_(auction_data["ID_ITEM"])
            item = Item(ID=item_data["ID"], NAME=item_data["NAME"])
            session.add(item)

        try:
            auction = Auction(ID=auction_data['ID'], ID_AUCTION=auction_data["ID_AUCTION"], ID_ITEM=auction_data["ID_ITEM"], PRICE=auction_data["PRICE"], QUANTITY=auction_data["QUANTITY"], TIME_LEFT=auction_data["TIME_LEFT"], DATETIME=now)
            #session.add(item)
            session.add(auction)
            session.commit()
        except Exception as ex:
            print(ex)
    

            

        #except:
        #    print("Sauvegarde des données impossible. Fonction auctions.")
            

    return 0

#Remet à 0 la BDD.
def init_bdd():
    conn = engine.connect()
    Base.metadata.drop_all(bind=conn)
    Base.metadata.create_all(bind=conn)
    return 0

#Sauvegarde les informations d'une auction dans la BDD.
def save_auctions(auction_data):
    Session = sessionmaker(bind=engine)
    session = Session()

    if not verify_item(auction_data["ID_ITEM"]):
        item_data = item_(auction_data["ID_ITEM"])
        item = Item(ID=item_data["ID"], NAME=item_data["NAME"])
        session.add(item)

    auction = Auction(ID=auction_data["ID"], ID_ITEM=auction_data["ID_ITEM"], PRICE=auction_data["PRICE"], QUANTITY=auction_data["QUANTITY"], TIME_LEFT=auction_data["TIME_LEFT"])
    #session.add(item)
    session.add(auction)
    session.commit()
    return 0

#Vérifie si un item existe déjà en BDD. 
def verify_item(id = 2):
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        item = session.query(Item).filter(Item.ID == id).first()
        print(item.NAME)
        return True
    except:
        print(f"Item ID={id} n'existe pas en base.")
        return False

#Récupère l'information d'un item dans l'API de Blizzard. 
def item_(id_item = 208212):

    token = createAccessToken().json()
    access_token = token['access_token']

    url = f"{baseURL}/data/wow/item/{id_item}?namespace=static-eu"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:
        res = json.loads(requests.get(url, headers=headers).content)
        item = {"ID": res['id'], "NAME": res['name']['fr_FR']}
    except:
        print(f'Item avec ID={id_item} non trouvé. Initialisé en BDD comme defaut.')
        item = {"ID": id_item, "NAME": "000"}
    
    return item

if __name__ == "__main__":
    #init_bdd()
    auctions()
