import oscP5.*;
import netP5.*;

OscP5 oscP5;
NetAddress loc;

String plotMode="line";

String IP = "127.0.0.1";
int SPIKE_DISPLAY_PORT = 1338;
String SPIKE_DISPLAY_ADDRESS = "/display_spikes";
SpikeSurface spikeSurface;

int displayWidth = 900;
int displayHeight = 600;

JSONObject linear2grid;

void setup() {
  oscP5 = new OscP5(this, SPIKE_DISPLAY_PORT); //Audience Port
  loc = new NetAddress(IP, SPIKE_DISPLAY_PORT); // send to self

  frameRate(20);
  //fullScreen();
  size(displayWidth, displayHeight);
  
  linear2grid = loadJSONObject("../../../data/linear2grid_400_20.json");
  
  background(100);
  spikeSurface = new SpikeSurface(20, 400, plotMode, displayWidth, displayHeight);
}

void draw() {
  spikeSurface.draw();
}
