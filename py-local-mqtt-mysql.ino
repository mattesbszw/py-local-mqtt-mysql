#include <DHT.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <time.h>

#define DHT_PIN 4
#define ONE_WIRE_BUS 16
#define DHTTYPE DHT11


DHT dht(DHT_PIN, DHTTYPE);
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

const char* ssid = "XXX";
const char* password = "XXX";

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

const char* MQTT_SERVER = "XXX";
const long MQTT_PORT = 1883;

const char MQTT_USERNAME[] = "student";            
const char MQTT_PASSWORD[] = "geheim";         
const char MQTT_CLIENTID[] = "esp32-var1-pub";
const char MQTT_TOPIC[] = "esp32/sensors";

const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 3600;
const int   daylightOffset_sec = 3600;

void setup(void){
  
  Serial.begin(115200);
  
  dht.begin(); 
  sensors.begin(); 

  connectWiFi();

  mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
  mqttClient.setBufferSize(2048);
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);

}

void connectWiFi(){
  
  WiFi.mode(WIFI_STA);
  Serial.print("Connecting to " + String(ssid));
  
  while(WiFi.status() != WL_CONNECTED){
    Serial.print(".");
    WiFi.begin(ssid, password); 
    delay(5000);     
  } 
  
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  
}

void mqttConnect(){

  while ( !mqttClient.connected() ){
    if ( mqttClient.connect( MQTT_CLIENTID, MQTT_USERNAME, MQTT_PASSWORD ) ) {
      Serial.print( "MQTT to " );
      Serial.print( MQTT_SERVER );
      Serial.print (" at port ");
      Serial.print( MQTT_PORT );
      Serial.println( " successful." );
    } else {
      Serial.print( "MQTT connection failed, rc = " );
      Serial.print( mqttClient.state() );
      Serial.println( " Will try again in a few seconds" );
      delay(1000);
    }
  }
}


void loop(void){ 

  if (WiFi.status() != WL_CONNECTED) {
      connectWiFi();
  }
  if (!mqttClient.connected()) {
     mqttConnect(); 
  }
  mqttClient.loop(); 
  
  
  /* process ds18b20 temperature => variable tmpDS contains ds temperature
   */
  sensors.requestTemperatures();
  float tmpD = sensors.getTempCByIndex(0);                  
  String tmpDS = String(tmpD);
  Serial.print("Sensor DS (*C): ");
  Serial.println(tmpDS); 


  /* process dht11 temperature => variable tmpDHT contains dht temperature
   */
  float tmp = dht.readTemperature();
  String tmpDHT = "-127.00";
  if (!isnan(tmp)) {
    tmpDHT = tmp;
  }
  Serial.print("Sensor DHT (*C): ");
  Serial.println(tmpDHT);
  

  /* process dht11 humidity => variable tmpHum contains dht humidity
   */
  float hum = dht.readHumidity();
  String tmpHum = "-127.00";
  if (!isnan(hum)) {
    tmpHum = hum;
  }
  Serial.print("Sensor DHT (% Hum): ");
  Serial.println(tmpHum);

  
  /* create timestamp => variable timebuf contains current timestamp
   */
  struct tm timeinfo;
  if(!getLocalTime(&timeinfo)){
    Serial.println("Failed to obtain time");
  }
  char timebuf[25];
  memset(timebuf, 0, sizeof(timebuf));
  strftime(timebuf,sizeof(timebuf), "%F %T", &timeinfo); // convert time structure to char and format
  
  /* 
   *  insert creation of JSONdoc and publishing here
   */


  
  delay(4000);
  
}
