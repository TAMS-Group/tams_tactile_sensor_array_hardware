l#include <SoftwareSerial.h>
#include <WireL.h>
 
#define bt_rxPin 10
#define bt_txPin 11
#define BLUETOOTH false
#define SERIAL true

//const int i2c_addresses[] = {1, 2, 3};
//const int i2c_addresses[] = {1, 3};
const int i2c_addresses[] = {1};
const int address_count = (sizeof(i2c_addresses) / sizeof(i2c_addresses[0]));

// must be greater than 0
//const byte sensor_numbers[address_count] = {1, 2, 3};  
//const byte sensor_numbers[address_count] = {1, 3};  
const byte sensor_numbers[address_count] = {1};  
//const byte sensor_byte_count[address_count] = {46, 46, 46};
//const byte sensor_byte_count[address_count] = {46, 46};
const byte sensor_byte_count[address_count] = {46};
int i;
#if BLUETOOTH
SoftwareSerial btSerial(bt_rxPin, bt_txPin);
#endif
void setup() {
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  digitalWrite(4, HIGH);
  digitalWrite(5, HIGH);
  
  Wire.begin();
  #if BLUETOOTH
  btSerial.begin(9600);
  #endif
  #if SERIAL
  Serial.begin(115200);
  #endif
}
 
void loop() {
  for(int n = 0; n < address_count; n++) {
    i = 1;
    byte storage[sensor_byte_count[n] + 1];
    storage[0] = sensor_numbers[n];
    Wire.requestFrom(i2c_addresses[n], sensor_byte_count[n]);    
    while (Wire.available()) {
      storage[i] = Wire.read();
      //Serial.println(storage[i]);
      i++;
    }
    //Serial.println(i);
    #if SERIAL
    Serial.write(storage, sensor_byte_count[n] + 1);
    #endif
    #if BLUETOOTH
    btSerial.write(storage, sensor_byte_count[n] + 1);
    #endif
  }
  // delay(100);
}
