#include <WireL.h>
#define i2c_address 3
#define SERIAL false

int analog_pins[] = {A0, A1, A3, A2, A6, A7}; 
int digital_pins[] = {7, 8, 9, 10, 11, 12}; 
const int analog_pin_count = (sizeof(analog_pins) / sizeof(analog_pins[0]));
const int digital_pin_count = (sizeof(digital_pins) / sizeof(digital_pins[0]));
const int len = int(ceil(analog_pin_count*digital_pin_count * 1.25));

// in this array, the 10bit values of the whole matrix are saved sequentially (zero-byte at the end)
// wwwwwwww|wwxxxxxx|xxxxyyyy|yyyyyyzz|zzzzzzzz|
byte storage[len+1];

void write_at(int value, int number){
  int i = (number % 4) * 2;
  int b = number * 1.25;
  //Serial.println(value);
  storage[b] = (storage[b] & byte(255 << (8 - i))) | (byte(value >> (2 + i)) & (255 >> i));
  storage[b+1] = (storage[b+1] & byte(255 >> (2+i))) | (byte(value << (6 - i)) & byte(255 << (6 - i)));
}
void requestEvent() {
  Wire.write(storage, len+1);
  //Serial.println(len+1);
}

void setup() {
  for(int i = 0; i < digital_pin_count; i++) {
    pinMode(digital_pins[i], INPUT);
  }
  storage[len] = 0;
  
  analogReference(EXTERNAL);
  Wire.begin(i2c_address);
  Wire.onRequest(requestEvent);
  #if SERIAL
  Serial.begin(115200); //9600); //
  #endif
}

void loop() {
  
  for(int i = 0; i < digital_pin_count; i++) {
    pinMode(digital_pins[i], OUTPUT);
    digitalWrite(digital_pins[i], HIGH);
    //delay(10);
    for(int j = 0; j < analog_pin_count; j++) {
      write_at(analogRead(analog_pins[j]), i * digital_pin_count + j);
    }
    pinMode(digital_pins[i], INPUT);
    //delay(10);
  }
  #if SERIAL
  // Serial.write((byte) 2);
  Serial.write(storage, len+1);
  #endif
  delay(10);

}
