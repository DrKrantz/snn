import oscP5.*;
import netP5.*;

OscP5 oscP5;
NetAddress loc;

String plotMode="line";

String IP = "localhost";
int SPIKE_DISPLAY_PORT = 1338;
String SPIKE_DISPLAY_ADDRESS = "/display_spikes";
SpikeSurface spikeSurface;

int displayWidth = 1600;
int displayHeight = 900;

JSONObject linear2grid;

void setup() {
  oscP5 = new OscP5(this, SPIKE_DISPLAY_PORT); //Audience Port
  loc = new NetAddress(IP, SPIKE_DISPLAY_PORT); // send to self

  frameRate(20);
  size(displayWidth, displayHeight);
  fullScreen(1);

  
  linear2grid = loadJSONObject("/Users/snn/snn/data/linear2grid_400_20.json");
  
  background(0);
  spikeSurface = new SpikeSurface(20, 400, plotMode, displayWidth, displayHeight);
}

void draw() {
  spikeSurface.draw();
}
