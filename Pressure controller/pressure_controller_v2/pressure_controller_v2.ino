/**
 * Pressure control software for the pressure regulator system.
 * 
 * 
 * Make sure that Tools > Board: "..." > Arduino ARM (32-bits) Boards > Arduino Due
 * (Programming Port) is selected before uploading new sketches. According to the
 * spec sheets, the valves have a response time of 6ms or less. We choose a response 
 * time of 10ms to be at the safe side. All pressures are given in mBar. The motor- 
 * driver for the pump needs a PWM input between 15-50kHz, 20kHz is recommended.
 * For the command list, look at process_serial_request() to find all possible input
 * commands. Feel free to add 
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
#define LCD_freq 2.5  // Hz
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
bool flag_once;
bool flag_continuous;
bool flag_spike;
bool flag_sleep;
int target_pressure;
int pulse_magnitude;
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
const float PV1_offset = -1.89;
const float PV2_offset = -1.89;

// Set the LCD address to 0x27 for a 16 chars and 2 line display
LiquidCrystal_I2C lcd(0x27, 16, 2);

// pin PC2 mapped to pin 34 on the DUE, this object uses PWM channel L0
pwm<pwm_pin::PWML0_PC2> pwm_pin34;  // PUMP_PRESSURE_PWM
// pin PC4 mapped to pin 36 on the DUE, this object uses PWM channel L1
pwm<pwm_pin::PWML1_PC4> pwm_pin36;  // PUMP_VACUUM_PWM


void setup() {
  // Arduino DUE baud rate
  Serial.begin(9600);

  // initialize the LCD and set timer for refresh rate
  lcd.begin();
  lcd.backlight();
  lcd.setCursor(0, 0); lcd.print("Setting up...");
  previous_LCD = millis();
  
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
  
  // Starting PWM signals
  pumps_PWM = 400;
  pwm_pin34.start(PUMP_PERIOD, PUMP_PRESSURE_PWM);
  pwm_pin36.start(PUMP_PERIOD, PUMP_VACUUM_PWM);

  // Open VALVE1 briefly to let pressure off tubing
  digitalWrite(VALVE1, HIGH); digitalWrite(LED1, LOW);
  delay(250);
  digitalWrite(VALVE1, LOW); digitalWrite(LED1, HIGH);
  delay(250);
  
  // Calculate pressure sensor offset that we correct for later
  PS1_output = 0;
  PS2_output = 0;
  for(int i=0; i<10000; i++){
    PS1_output = PS1_output - analogRead(PressureSensor1);
    PS2_output = PS2_output - analogRead(PressureSensor2);
  }
  PS1_offset = voltage2pressure(PS1_output/10000);
  PS2_offset = voltage2pressure(PS2_output/10000);
  Serial.print("PS1 offset: "); Serial.print(PS1_offset); Serial.println(" mBar");
  Serial.print("PS2 offset: "); Serial.print(PS2_offset); Serial.println(" mBar");
  
  target_pressure = 0;
  flag_once = true;
  flag_continuous = true;
  flag_spike = false;
  flag_sleep = false;
  lcd.clear();
}


void loop() {
  
  // Process serial requests:
  if (Serial.available()) {
    process_serial_request();
  }
  
  // Read out pressure sensors, average, and convert to pressure
  read_pressure_sensors();
  
  // Update LCD at a rate of LCD_freq
  update_lcd();

  //// To do only once
  if (flag_once) {
    flag_once = false;
    
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
          change_duty(pwm_pin34, 400, PUMP_PERIOD);
          delay(5);
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
          change_duty(pwm_pin36, 400, PUMP_PERIOD);
          delay(5);
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
      pumps_PWM = 500;
    } else if (abs(target_pressure) <= 100) {
      pumps_PWM = 1000;
    } else if (abs(target_pressure) <= 150) {
      pumps_PWM = 1500;
    } else if (abs(target_pressure) > 150) {
      pumps_PWM = 1800;
    }
  }
  
  //// To do when spike
  if (flag_spike) {
    flag_spike = false;
    
    // close the valve after the pressure tank
    digitalWrite(VALVE2, HIGH); digitalWrite(LED2, LOW);
    delay(10);
    
    // built up pressure in the pressure tank
    if (pulse_magnitude > 0) {
      Serial.println("Positive pulse");
      // compensate if pressure is too high
      if (pulse_magnitude - P2 > -MARGIN) {
        digitalWrite(VALVE1, LOW); digitalWrite(LED1, HIGH);
        change_duty(pwm_pin34, 0, PUMP_PERIOD);
        change_duty(pwm_pin36, 400, PUMP_PERIOD);
        while (P2 > pulse_magnitude) {
          read_pressure_sensors();
        }
      }
      // actually buildup pressure
      digitalWrite(VALVE1, HIGH); digitalWrite(LED1, LOW);
      change_duty(pwm_pin34, 1900, PUMP_PERIOD);
      change_duty(pwm_pin36, 0, PUMP_PERIOD);
      while (P2 < pulse_magnitude) {
        read_pressure_sensors();
      }
      change_duty(pwm_pin34, 0, PUMP_PERIOD);
    } else if (pulse_magnitude < 0) {
      Serial.println("Negative pulse");
      // compensate if pressure is too low
      if (pulse_magnitude - P2 > MARGIN) {
        digitalWrite(VALVE1, HIGH); digitalWrite(LED1, LOW);
        change_duty(pwm_pin34, 400, PUMP_PERIOD);
        change_duty(pwm_pin36, 0, PUMP_PERIOD);
        while (P2 < pulse_magnitude) {
          read_pressure_sensors();
        }
      }
      // actually buildup pressure
      digitalWrite(VALVE1, LOW); digitalWrite(LED1, HIGH);
      change_duty(pwm_pin34, 0, PUMP_PERIOD);
      change_duty(pwm_pin36, 1900, PUMP_PERIOD);
      while (P2 > pulse_magnitude) {
        read_pressure_sensors();
      }
      change_duty(pwm_pin36, 0, PUMP_PERIOD);
    }
    
    // open valve after the pressure tank briefly
    digitalWrite(VALVE2, LOW); digitalWrite(LED2, HIGH);
    delay(300);
    digitalWrite(VALVE2, HIGH); digitalWrite(LED2, LOW);
  }
  
  
  //// To do continuous
  // Set vacuum pump dutycycle
  if (target_pressure < -MARGIN) {
    if (P2-MARGIN > target_pressure) {
      change_duty(pwm_pin36, pumps_PWM, PUMP_PERIOD);
      delay(100);
    } else {
      change_duty(pwm_pin36, 0, PUMP_PERIOD);
    }
  }
  // Set pressure pump dutycycle
  else if (target_pressure > MARGIN) {
    if (P2+MARGIN < target_pressure) {
      change_duty(pwm_pin34, pumps_PWM, PUMP_PERIOD);
      delay(100);
    } else {
      change_duty(pwm_pin34, 0, PUMP_PERIOD);
    }
  }
  
  
  //// To do when idle
  if (flag_sleep) {
    lcd.clear();
    change_duty(pwm_pin34, 0, PUMP_PERIOD);
    change_duty(pwm_pin36, 0, PUMP_PERIOD);
    digitalWrite(VALVE1, LOW); digitalWrite(LED1, HIGH);
    digitalWrite(VALVE2, LOW); digitalWrite(LED2, HIGH);
    delay(10);
    lcd.noBacklight();
    
    while (flag_sleep) {
      process_serial_request();
    }
    setup();
  }
  
}


void read_pressure_sensors() {
  PS1_output = 0;
  PS2_output = 0;
  for (int i=0; i<10; i++){
    PS1_output = PS1_output - analogRead(PressureSensor1);
    PS2_output = PS2_output - analogRead(PressureSensor2);
  }
  
  // correct for pressure sensor offset
  P1 = voltage2pressure(PS1_output/10) - PS1_offset;
  P2 = voltage2pressure(PS2_output/10) - PS2_offset;

  // correct for offset from valves
  if (digitalRead(VALVE1)) {
    P1 = P1 - PV1_offset;
    P2 = P2 - PV1_offset;
  }
  if (digitalRead(VALVE2)) {
    P1 = P1 - PV2_offset;
    P2 = P2 - PV2_offset;
  }
  
  // Send out pressur readout over serial port every X ms
  Serial.println((String)"PS "+P1+" "+P2);
}


void update_lcd() {
  current = millis();
  if (current - previous_LCD >= refresh_time) {
    previous_LCD = current;
    lcd.setCursor(0,0); lcd.print((String)P1+" mBar   ");
  }
}


void process_serial_request() {
  // flush input buffer so that we only read the last input
  while (Serial.available()) {
    command = Serial.readStringUntil('\n');
    command1 = getValue(command, ' ', 0);
    command2 = getValue(command, ' ', 1);
    Serial.print(command1+" "); Serial.println(command2);
  }
    if (command1 == "P") {
      // set pressure
      target_pressure = command2.toFloat();
      flag_once = true;
      flag_continuous = true;
      flag_spike = false;
    } else if(command1 == "S") {
      // make pressure spike
      pulse_magnitude = command2.toFloat();
      target_pressure = 0;
      flag_once = false;
      flag_continuous = false;
      flag_spike = true;
    } else if (command1 == "IDLE") {
      // set device idle
      flag_sleep = true;
    } else if (command1 == "W8KE") {
      // wake-up device
      flag_sleep = false;
    } else if (command1 == "V2H") {
      digitalWrite(VALVE2, HIGH); digitalWrite(LED2, LOW);
    } else if (command1 == "V2L") {
      digitalWrite(VALVE2, LOW); digitalWrite(LED2, HIGH);
    } else if (command1 == "V1H") {
      digitalWrite(VALVE1, HIGH); digitalWrite(LED1, LOW);
    } else if (command1 == "V1L") {
      digitalWrite(VALVE1, LOW); digitalWrite(LED1, HIGH);
    } else if (command1 == "PPON") {
      change_duty(pwm_pin34, 1900, PUMP_PERIOD);
    } else if (command1 == "PPOFF") {
      change_duty(pwm_pin34, 0, PUMP_PERIOD);
    } else if (command1 == "PVON") {
      change_duty(pwm_pin36, 1900, PUMP_PERIOD);
    } else if (command1 == "PVOFF") {
      change_duty(pwm_pin36, 0, PUMP_PERIOD);
    } else if (command1 == "DIM") {
      lcd.noBacklight();
    } else if (command1 == "LCD") {
      lcd.backlight();
    }
}
 
