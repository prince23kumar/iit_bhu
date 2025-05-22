void setup() {
  Serial.begin(115200);
  randomSeed(analogRead(0)); // Randomize seed using floating analog pin
}

void loop() {
  int red = random(500, 1000);
  int ir = random(500, 1000);
  int green = random(500, 1000);
  int heartrate = random(60, 100);
  int spo2 = random(90, 100);
  int ecg = random(300, 800);
  float temp1 = random(360, 380) / 10.0;
  float temp2 = random(360, 380) / 10.0;
  float temp3 = random(360, 380) / 10.0;
  int gas1 = random(100, 500);
  int gas2 = random(100, 500);
  int gas3 = random(100, 500);
  int gas4 = random(100, 500);
  int gas5 = random(100, 500);
  int dat1 = random(10, 50);

  Serial.print(red); Serial.print(",");
  Serial.print(ir); Serial.print(",");
  Serial.print(green); Serial.print(",");
  Serial.print(heartrate); Serial.print(",");
  Serial.print(spo2); Serial.print(",");
  Serial.print(ecg); Serial.print(",");
  Serial.print(temp1, 1); Serial.print(",");
  Serial.print(temp2, 1); Serial.print(",");
  Serial.print(temp3, 1); Serial.print(",");
  Serial.print(gas1); Serial.print(",");
  Serial.print(gas2); Serial.print(",");
  Serial.print(gas3); Serial.print(",");
  Serial.print(gas4); Serial.print(",");
  Serial.print(gas5); Serial.print(",");
  Serial.println(dat1);

  delay(1000); // Wait for 1 second
}
