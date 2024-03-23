#include <Wire.h> 
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27,16,2);  // set the LCD address to 0x27 for a 16 chars and 2 line display


byte customChar[8] = {
	0b01100,
	0b01100,
	0b00000,
	0b01110,
	0b11100,
	0b01100,
	0b11010,
	0b10011
};

void createCustomChar(String input, int charIndex){
  if(input.length() != 40){
    // invalid Char
    return;
  }
  byte customChar[8];

    for(int i = 0; i < 8; i++){
        String byteString = input.substring(i*5, i*5+5);
        byteString.replace("0", " ");
        byteString.replace("1", "0");
        byteString.replace(" ", "1");
        customChar[i] = strtol(byteString.c_str(), NULL, 2);
    }
    lcd.createChar(charIndex,customChar);

}
 
 void setup()
{
  lcd.init();   
  lcd.backlight();
  lcd.setCursor(0,0);
  lcd.print("Hello, World");
  createCustomChar("0000011111000001111100000111110000011111");
  lcd.setCursor(13,0);
  lcd.write(0);

}

void loop(){}