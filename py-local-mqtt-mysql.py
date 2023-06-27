import mysql.connector as mariadb
import paho.mqtt.client as mqtt 
import json

MQTT_SERVER_IP = "10.10.10.X"
MQTT_PORT = 1883

MQTT_USER_NAME = "XXX"
MQTT_USER_PASS = "XXX"
MQTT_CLIENT_ID = "py-mqtt-mysql"
MQTT_TOPIC = "esp32/sensors"

MYSQL_HOST = "192.168.X.X"
MYSQL_USER = "XXX"
MYSQL_PASS = "XXX"
MYSQL_SCHEME = "XXX"

class ThingSpeakPayload(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j) # deserializes binary json string from subscription into a dictionary
## end class definition

def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    print("Connected with result code {0}".format(str(rc)))
    client.subscribe(MQTT_TOPIC)
## end on_connect function


def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.

    print("Message received-> " + msg.topic)

    obj = ThingSpeakPayload(msg.payload)

    if obj.field1=='nan':
        obj.field1='NULL'

    if obj.field2==-127:
        obj.field2='NULL'
        
    mytimestamp = obj.created_at.replace("T", " ")
    mytimestamp = mytimestamp.replace("Z", "")

    
    sql = """INSERT INTO itt_sensors (ds, dht, created) VALUES (%s,%s,%s)"""
    args = (obj.field1, obj.field2, mytimestamp)
    
    print(sql)
    print(args)
    
    # Save Data into DB Table
    try:
        cursor.execute(sql, args)
    except mariadb.Error as error:
        print("Error: {}".format(error))

    mariadb_connection.commit()    
## end on_message function
    

## main routine

mariadb_connection = mariadb.connect(user=MYSQL_USER, password=MYSQL_PASS, host=MYSQL_HOST, database=MYSQL_SCHEME)
cursor = mariadb_connection.cursor()

client = mqtt.Client(MQTT_CLIENT_ID) #create new instance
client.username_pw_set(username=MQTT_USER_NAME,password=MQTT_USER_PASS)

client.on_connect = on_connect  # Define callback function for successful connection
client.on_message = on_message  # Define callback function for receipt of a message

client.connect(MQTT_SERVER_IP, MQTT_PORT)
client.loop_forever()  # Start networking daemon

