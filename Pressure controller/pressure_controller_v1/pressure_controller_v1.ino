/**
 * Pressure control software for the pressure regulator system.
 * 
 * 
 * Make sure that Tools > Board: "..." > Arduino ARM (32-bits) Boards > Arduino Due
 * (Programming Port) is selected before uploading new sketches. According to the
 * spec sheets, the valves have a response time of 6ms or less. We choose a response 
 * time of 10ms to be at the safe side. All pressures are given in mBar. The motor- 
 * driver for the pump needs a PWM input between 15-50kHz, 20kHz is recommended.
 * 
 * External libraries 'pwm_lib' and 'tc_lib' were downloaded here:
 * https://github.com/antodom/pwm_lib
 * https://github.com/antodom/tc_lib
 * 
 * Important parameters are:
 * MARGIN:    defines the margin of pressure fluctuation allowed as the range: 
 *            [-MARGIN, MARGIN] in mBar. Note that the pressure sensor output
 *            fluctuates ~5mBar at ATM from noise.
 * LCD_freq:  defines the frequency for updating the LCD display in Hz.
 * 
 * 
 * The Brinks Lab, by Thijs van der Burgt
 * 
 */
#include <Wire.h> 
#include <LiquidCrystal_I2C.h>
#include "pwm_lib.h"
using namespace arduino_due::pwm_lib;

#define MARGIN 5    // pressure can vary [-margin, margin]
#define LCD_freq 5  // Hz
#define LED1 14
#define LED2 15
#define VALVE1 30
#define VALVE2 32
#define PressureSensor1 A0
#define PressureSensor2 A1
// defining signalling period and duty cycle per pin
#define PUMP_PERIOD         2000  // 1e-8 seconds
#define PUMP_PRESSURE_PWM   0     // 1e-8 seconds
#define PUMP_VACUUM_PWM     0     // 1e-8 seconds

String command;
String command1;
String command2;
bool flag;
int target_pressure;
int pumps_PWM;
int PS1_output;
int PS2_output;
float PS1_offset;
float PS2_offset;
float P1;
float P2;
float dP;
unsigned long previous_LCD, current;
const long refresh_time = 1000/LCD_freq;

// Set the LCD address to 0x27 for a 16 chars and 2 line display
LiquidCrystal_I2C lcd(0x27, 16, 2);

// pin PC2 mapped to pin 34 on the DUE, this object uses PWM channel L0
pwm<pwm_pin::PWML0_PC2> pwm_pin34;
// pin PC4 mapped to pin 36 on the DUE, this object uses PWM channel L1
pwm<pwm_pin::PWML1_PC4> pwm_pin36;


void setup() {
  // Arduino DUE baud rate
  Serial.begin(9600);
  
  // Arduino DUE can read 12 bits instead of default 10
  analogReadResolution(12);
  
  pinMode(LED1, OUTPUT);
  pinMode(LED2, OUTPUT);
  pinMode(VALVE1, OUTPUT);
  pinMode(VALVE2, OUTPUT);
  pinMode(PressureSensor1, INPUT);
  pinMode(PressureSensor2, INPUT);
  
  // LEDs are inverted so adapter delivers required current
  digitalWrite(VALVE1, LOW); digitalWrite(LED1, HIGH);
  digitalWrite(VALVE2, LOW); digitalWrite(LED2, HIGH);
  
  // initialize the LCD
  lcd.begin();
  lcd.backlight();
  lcd.setCursor(0, 0); lcd.print("Setting up...");
  
  // Starting PWM signals
  pwm_pin34.start(PUMP_PERIOD, PUMP_PRESSURE_PWM);
  pwm_pin36.start(PUMP_PERIOD, PUMP_VACUUM_PWM);
//  change_duty(pwm_pin34, PUMP_PRESSURE_PWM, PUMP_PERIOD);
//  change_duty(pwm_pin36, PUMP_VACUUM_PWM, PUMP_PERIOD);

  // Open VALVE1 briefly to let pressure off tubing
  digitalWrite(VALVE1, HIGH); digitalWrite(LED1, LOW);
  delay(500);
  digitalWrite(VALVE1, LOW); digitalWrite(LED1, HIGH);
  delay(500);

  // Calculate pressure sensor offset that we correct for later
  for(int i=0; i<1000; i++){
    PS1_output = PS1_output + analogRead(PressureSensor1);
    PS2_output = PS2_output + analogRead(PressureSensor2);
  }
  PS1_offset = voltage2pressure(PS1_output/1000);
  PS2_offset = voltage2pressure(PS2_output/1000);
  Serial.print("PS1 offset: "); Serial.print(PS1_offset); Serial.println(" mBar");
  Serial.print("PS2 offset: "); Serial.print(PS2_offset); Serial.println(" mBar");

  // Udate LCD and start timer for refresh rate
  previous_LCD = millis();
  lcd.setCursor(0,1); lcd.print("Setup complete");
  lcd.clear();
  
  target_pressure = 0;
  flag = true;
  
}


void loop() {
  
  // Read out pressure sensors, average, and convert to pressure
  read_pressure_sensors();
  
  // Update LCD at a rate of LCD_freq
  current = millis();
  if (current - previous_LCD >= refresh_time) {
    previous_LCD = current;
    lcd.setCursor(0,0); lcd.print((String)P1+" mBar   ");
  }

  // Process serial requests:
  if (Serial.available()) {
    process_serial_request();
  }

  //// To do only once
  if (flag) {
    flag = false;
    
    // target_pressure: ATM
    if (target_pressure == 0){
      Serial.println("ATM, pumps off");
      digitalWrite(VALVE2, HIGH); digitalWrite(LED2, LOW);
      delay(10);
      change_duty(pwm_pin34, 0, PUMP_PERIOD);
      change_duty(pwm_pin36, 0, PUMP_PERIOD);
    }
    // target_pressure: <ATM
    else if (target_pressure < 0) {
      if (target_pressure - P2 > MARGIN) {
        // bring pressure up to target_pressure
        digitalWrite(VALVE1, HIGH); digitalWrite(LED1, LOW);
        delay(10);
        Serial.print("Compensation upward: ");
        Serial.println(P2);
        while (target_pressure - P2 > MARGIN) {
          read_pressure_sensors();
          change_duty(pwm_pin34, 300, PUMP_PERIOD);
          delay(10);
        }
      }
      digitalWrite(VALVE1, LOW); digitalWrite(LED1, HIGH);
      digitalWrite(VALVE2, LOW); digitalWrite(LED2, HIGH);
      delay(10);
      change_duty(pwm_pin34, 0, PUMP_PERIOD);
    }
    // target_pressure: >ATM
    else if (target_pressure > 0){
      if (target_pressure - P2 < -MARGIN) {
        // bring pressure down to target_pressure
        digitalWrite(VALVE1, LOW); digitalWrite(LED1, HIGH);
        delay(10);
        Serial.print("Compensation downward: ");
        Serial.println(P2);
        while (target_pressure - P2 < -MARGIN) {
          read_pressure_sensors();
          change_duty(pwm_pin36, 300, PUMP_PERIOD);
          delay(10);
        }
      }
      digitalWrite(VALVE1, HIGH); digitalWrite(LED1, LOW);
      digitalWrite(VALVE2, LOW); digitalWrite(LED2, HIGH);
      delay(10);
      change_duty(pwm_pin36, 0, PUMP_PERIOD);
    }
    
    // Increase dutycycle of pumps with increasing target pressure,
    // substitute this functinoality with PID in the future!
    if (abs(target_pressure) <= 50) {
      pumps_PWM = 300;
    } else if (abs(target_pressure) <= 100) {
      pumps_PWM = 600;
    } else if (abs(target_pressure) <= 200) {
      pumps_PWM = 1000;
    } else if (abs(target_pressure) <= 300) {
      pumps_PWM = 1400;
    } else if (abs(target_pressure) > 300) {
      pumps_PWM = 1800;
    }
    
  }

  //// To do continuous
  // Set vacuum pump dutycycle
  if (target_pressure < -MARGIN) {
    if (P2-MARGIN > target_pressure) {
      change_duty(pwm_pin36, pumps_PWM, PUMP_PERIOD);
    } else {
      change_duty(pwm_pin36, 0, PUMP_PERIOD);
    }
  }
  // Set pressure pump dutycycle
  else if (target_pressure > MARGIN) {
    if (P2+MARGIN < target_pressure) {
      change_duty(pwm_pin34, pumps_PWM, PUMP_PERIOD);
    } else {
      change_duty(pwm_pin34, 0, PUMP_PERIOD);
    }
  }
  
}


void read_pressure_sensors() {
  PS1_output = 0;
  PS2_output = 0;
  for (int i=0; i<10; i++){
    PS1_output = PS1_output + analogRead(PressureSensor1);
    PS2_output = PS2_output + analogRead(PressureSensor2);
  }
  P1 = voltage2pressure(PS1_output/10) - PS1_offset;
  P2 = voltage2pressure(PS2_output/10) - PS2_offset;
  
  // Send out pressur readout over serial port every X ms
  Serial.println((String)"PS "+P1+" "+P2);
}

void process_serial_request() {
  // flush input buffer so that we only read the last input
  while (Serial.available()) {
    command = Serial.readStringUntil('\n');
  }
    command1 = getValue(command, ' ', 0);
    command2 = getValue(command, ' ', 1);
    Serial.print(command1+" "); Serial.println(command2);
    if (command1 == "P") {
      target_pressure = command2.toFloat();
      flag = true;
    }
}
 
