import oscP5.*;
import netP5.*;

OscP5 oscP5;
NetAddress loc;

String plotMode="line";

String IP = "localhost";
int SPIKE_DISPLAY_PORT = 1338;
String SPIKE_DISPLAY_ADDRESS = "/display_spikes";
SpikeSurface spikeSurface;

int displayWidth = 1280;
int displayHeight = 720;

JSONObject linear2grid;

void setup() {
  oscP5 = new OscP5(this, SPIKE_DISPLAY_PORT); //Audience Port
  loc = new NetAddress(IP, SPIKE_DISPLAY_PORT); // send to self

  frameRate(20);
  //size(displayWidth, displayHeight);
  fullScreen();

  
  linear2grid = loadJSONObject("../../../data/linear2grid_400_20.json");
  
  background(100);
  spikeSurface = new SpikeSurface(20, 400, plotMode, displayWidth, displayHeight);
}

void draw() {
  spikeSurface.draw();
}
