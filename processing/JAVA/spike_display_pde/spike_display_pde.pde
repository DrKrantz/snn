import oscP5.*;
import netP5.*;

OscP5 oscP5;
NetAddress loc;


String IP = "127.0.0.1";
int SPIKE_DISPLAY_PORT = 1338;
String SPIKE_DISPLAY_ADDRESS = "/display_spikes";
SpikeSurface spikeSurface;


class SpikeSurface {
  PGraphics surface;
  int circleSize = 5;
  int lineWidth = 8;
  int border = 5;
  int sWidth, sHeight, pos_x, pos_y;
  int nCol, nRow, xDist, yDist;
  String plotMode;
  JSONArray fired = new JSONArray();
  
  
  SpikeSurface(int nCol, int n, String plotMode, int sWidth, int sHeight) {
    this.nCol = nCol;
    this.nRow = ceil(n/nCol);
    this.xDist = (sWidth-2*this.border) / this.nCol;
    this.yDist = (sHeight-2*this.border) / this.nRow;
    this.pos_x = 0;
    this.pos_y = 0;
    this.plotMode = plotMode;
    this.surface = createGraphics(sWidth, sHeight);
    this.surface.smooth();
  }
  
  void draw() {
    this.surface.beginDraw();
    this.surface.background(0);
    this.surface.strokeWeight(10);
    this.surface.stroke(0, 255, 0);
    
    if ( this.fired.size() > 0 ) {
      for(int n=0; n < this.fired.size(); n++) {
        int id = this.fired.getInt(n);
        println(id);
      }
    }
    
    this.surface.endDraw();
    image(this.surface, this.pos_x, this.pos_y);
    this.set_fired(new JSONArray());
  }
  
  public void set_fired(JSONArray fired) {
    this.fired = fired; // TODO should be appended
  }
}



void setup() {
  oscP5 = new OscP5(this, SPIKE_DISPLAY_PORT); //Audience Port
  loc = new NetAddress(IP, SPIKE_DISPLAY_PORT); // send to self
  
  
  frameRate(20);
  //fullScreen();
  size(1280, 720);
  background(100);
  spikeSurface = new SpikeSurface(10, 100, "line", 1280,  720);
  
  
  
}

void draw() {
  spikeSurface.draw();
}
