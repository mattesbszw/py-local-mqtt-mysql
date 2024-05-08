import mysql.connector as mariadb
import paho.mqtt.client as mqtt 
import json

### hier Ihre RPI-Adresse eintragen
MQTT_SERVER_IP = "10.10.10.X"
MQTT_PORT = 1883

### Datenbank-Verbindung anpassen
MYSQL_HOST = "bszw.usw..."
MYSQL_USER = "wit11x"
MYSQL_PASS = "XXX"
MYSQL_SCHEMA = "wit11x_nachname"

### MQTT-Zugangsdaten sollten so passen
MQTT_USER = "student"
MQTT_PASS = "geheim"
MQTT_CLIENT_ID = "py-mqtt-mysql"
MQTT_TOPIC = "esp32/sensors"

class ThingSpeakPayload(object):
	def __init__(self, j):
		self.__dict__ = json.loads(j) # deserializes binary json string from subscription into a dictionary
## end class definition

def on_connect(client, userdata, flags, reason_code, properties):  # The callback for when the client connects to the broker
	print("Connected: {0}".format(reason_code))  # Print result of connection attempt
	client.subscribe(MQTT_TOPIC)
## end on_connect function


def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.

	print("Message received-> " + msg.topic)

	obj = ThingSpeakPayload(msg.payload)

	# vom Broker gelieferte Werte 1:1 auf der Konsole ausgeben
	print(obj.channel_id)
	print(obj.created_at)
	print(obj.field1)
	print(obj.field2)
	print(obj.field3)

	insert_sensor_values_into_mysql(obj.channel_id, obj.field1, obj.field2, obj.field3, obj.created_at)

## end on_message function

def insert_sensor_values_into_mysql(channelID, ds_temp, dht_temp, dht_hum, created_at):

	mariadb_connection = mariadb.connect(user=MYSQL_USER, password=MYSQL_PASS, host=MYSQL_HOST, database=MYSQL_SCHEMA)
	cursor = mariadb_connection.cursor()

	# Error-Handling
	# field1: ds-sensor => worst case -127.0
	# field2 und field: dht => worst case 'nan' (not a number)
	if ds_temp=='-127.0':
		ds_temp=None
	if dht_temp=='nan':
		dht_temp=None
	if dht_hum=='nan':
		dht_hum=None
        
	# Zeitstempel von Thingspeak anpassen, dass er von der Datenbank akzeptiert wird (kein T in der Mitte, kein Z am Ende)
	mytimestamp = created_at.replace("T", " ")
	mytimestamp = mytimestamp.replace("Z", "")
       
	sql = """INSERT INTO itt_sensors (ds_temp, 
                         dht_temp, 
                         dht_hum, 
                         created) 
             VALUES (%s, %s, %s, %s);"""
      
	print(sql)
	
	args = (ds_temp, dht_temp, dht_hum, mytimestamp)
	print(args)
	
	# execute: Speichern der Werte
	# commit: DB-Transaktion beenden und Änderungen übernehmen
	try:
		cursor.execute(sql, args)
	except mariadb.Error as error:
		print("Error: {}".format(error))

	mariadb_connection.commit()        

## end insert mysql function
    

## main routine

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, MQTT_CLIENT_ID) #create new instance
client.username_pw_set(username=MQTT_USER,password=MQTT_PASS)

client.on_connect = on_connect  # Define callback function for successful connection
client.on_message = on_message  # Define callback function for receipt of a message

client.connect(MQTT_SERVER_IP, MQTT_PORT)
client.loop_forever()  # Start networking daemon

