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
  int sWidth;
  int sHeight;
  int nCol;
  int nRow;
  int xDist;
  int yDist;
  String plotMode;
  
  
  SpikeSurface(int nCol, int n, String plotMode, int sWidth, int sHeight) {
    this.nCol = nCol;
    this.nRow = ceil(n/nCol);
    this.xDist = (sWidth-2*this.border) / this.nCol;
    this.yDist = (sHeight-2*this.border) / this.nRow;
    this.plotMode = plotMode;
    this.surface = createGraphics(sWidth, sHeight);
    this.surface.smooth();
  }
  
  void draw() {
    this.surface.beginDraw();
    this.surface.stroke(0, 255, 0);
    this.surface.strokeWeight(10);
    this.surface.line(0, 0, 200, 200);
  }
}



void setup() {
  frameRate(20);
  size(1280, 720);
  background(100);
  spikeSurface = new SpikeSurface(10, 100, "line", 1280,  720);
}

void draw() {
  spikeSurface.draw();
}
