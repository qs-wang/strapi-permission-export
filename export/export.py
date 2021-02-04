import psycopg2
from psycopg2.extras import RealDictCursor
import json
import os

def db_connector(func):
    def with_connection_(*args,**kwargs):
        # conn_str = conn_str
        cnn = psycopg2.connect(
            "dbname=strapi user={0} password={1} host=localhost".format(os.getenv('STRAPI_DB_USER'), os.getenv('STRAPI_DB_PASS')) , 
        cursor_factory=RealDictCursor)
        try:
            rv = func(cnn, *args,**kwargs)
        except Exception:
            cnn.rollback()
            # logging.error("Database connection error")
            raise
        else:
            cnn.commit()
        finally:
            cnn.close()        
        
        return rv
    return with_connection_

@db_connector
def fetch_data_and_export(cnn):
    index_document = []
    cur = cnn.cursor()
    authJson = {}
    publicJson={}
    cur.execute('SELECT type, controller, action,enabled,role FROM "public"."users-permissions_permission" where type=\'application\' and (role =1 or role=2) order by controller,  action, role', ()) 
    for row in cur:
        roleId = row.get('role')
        controller = row.get('controller')
        type = row.get('type')
        action = row.get('action')
        enabled = row.get('enabled')
        if roleId == 1:
            if type not in authJson:
                authJson[type] = {}

            if controller  not in authJson[type]:
                authJson[type][controller] = {}
        
            authJson[type][controller][action] = {
                    'enabled': enabled
            }

        if roleId == 2:
            if type not in publicJson:
                publicJson[type] = {}

            if controller  not in publicJson[type]:
                publicJson[type][controller] = {}
        
            publicJson[type][controller][action] = {
                    'enabled': enabled
            }
            

    with open('output/permission.js', 'w', encoding='utf8') as json_file:
        json.dump({
            'public': publicJson,
            'authenticated': authJson
        }, json_file, ensure_ascii=False)
