import oscP5.*;
import netP5.*;

OscP5 oscP5;
NetAddress loc;

String ip = "127.0.0.1";
int port = 1338;

void setup() {
  
  size(640, 360);
  background(102);
  
  oscP5 = new OscP5(this, port); //Audience Port
  loc = new NetAddress(ip, port); // send to self
}
