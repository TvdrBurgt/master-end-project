float voltage2pressure(float nbits){
  float Vsupply = 5; // Volt
  float Vout;
  float Ppsi;
  float Pmbar;

  Vout = nbits/pow(2,12)*Vsupply;
  Ppsi = (Vout - 0.1*Vsupply)/(0.8*Vsupply)*30 - 15;
  Pmbar = 68.9475729*Ppsi;
  
  return Pmbar;
}
