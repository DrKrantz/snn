class SpikeSurface {
  PGraphics surface;
  int circleSize = 5;
  int lineWidth = 8;
  int border = 5;
  int sWidth, sHeight, pos_x, pos_y;
  int nCol, nRow;
  float xDist, yDist;
  String plotMode = "dot";
  JSONArray fired = new JSONArray();


  SpikeSurface(int nCol, int n, String plotMode, int sWidth, int sHeight) {
    this.nCol = nCol;
    this.nRow = ceil(n/nCol);
    this.xDist = float(sWidth-2*this.border) / float(this.nCol);
    this.yDist = float(sHeight-2*this.border) / float(this.nRow);
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

    if (this.fired.size() == 1) {
      this.drawPoint(this.fired.getString(0));
    } else if ( this.fired.size() > 1 ) {
      if (this.plotMode.equals("dot") == true) {
        for (int n=0; n < this.fired.size(); n++) {
          String neuron_id = this.fired.getString(n);
          this.drawPoint(neuron_id);
        }
      } else if (this.plotMode.equals("line") == true) {
        println("Not ye implements", this.plotMode);
      } else {
        println("Unknown plotmode", this.plotMode);
      }
    }
    this.surface.endDraw();
    image(this.surface, this.pos_x, this.pos_y);
    this.set_fired(new JSONArray());
  }
  
  void drawPoint(String neuron_id) {
    int colId = getCoord(neuron_id, 0);
    int rowId = getCoord(neuron_id, 1);
    int x = round(this.border + rowId*this.xDist);
    int y = round(this.border + colId*this.yDist);
    this.surface.circle(x, y, this.circleSize);
  }
  

  public void set_fired(JSONArray fired) {
    this.fired = fired; // TODO should be appended
  }
}

int getCoord(String neuron_id, int idx) {
  JSONArray coords = (JSONArray) linear2grid.get(neuron_id);
  return coords.getInt(idx);
}
