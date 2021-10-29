import oscP5.*;
import netP5.*;

OscP5 oscP5;
NetAddress loc;

String IP = "127.0.0.1";
int SPIKE_DISPLAY_PORT = 1338;
String SPIKE_DISPLAY_ADDRESS = "/display_spikes";
SpikeSurface spikeSurface;


JSONObject linear2grid;

void setup() {
  oscP5 = new OscP5(this, SPIKE_DISPLAY_PORT); //Audience Port
  loc = new NetAddress(IP, SPIKE_DISPLAY_PORT); // send to self

  frameRate(20);
  //fullScreen();
  size(1280, 720);
  
  linear2grid = loadJSONObject("../../../data/linear2grid_400_20.json");
  
  background(100);
  spikeSurface = new SpikeSurface(10, 100, "line", 1280, 720);
}

void draw() {
  spikeSurface.draw();
}
