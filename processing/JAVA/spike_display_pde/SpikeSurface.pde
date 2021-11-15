import java.util.Collections;

class SpikeSurface {
  PGraphics surface;
  int circleSize = 5;
  int lineWidth = 2;
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
    this.surface.strokeWeight(this.lineWidth);
    this.surface.stroke(0, 255, 0);
  }

  void draw() {
    this.surface.beginDraw();
    this.surface.background(0);

    // copy this.fired to prevent override while draw is running
    // convert JSONArray to IntList to shuffle the list 
    IntList currentFired = new IntList();
    for (int i=0; i<this.fired.size(); i++) {
      currentFired.append( (int) this.fired.get(i) );
    }
    currentFired.shuffle();
    this.set_fired(new JSONArray());

    if (currentFired.size() == 1) {
      this.drawPoint((int) currentFired.get(0));
    } else if ( currentFired.size() > 1 ) {
      if (this.plotMode.equals("dot") == true) {
        for (int n=0; n < currentFired.size(); n++) {
          int neuron_id = (int) currentFired.get(n);
          this.drawPoint(neuron_id);
        }
      } else if (this.plotMode.equals("line") == true) {
        ArrayList xVals = new ArrayList();
        ArrayList yVals = new ArrayList();
        for (int n=0; n < currentFired.size(); n++) {
          int neuron_id = (int) currentFired.get(n);
          int colId = getCoord(neuron_id, 0);
          int rowId = getCoord(neuron_id, 1);
          xVals.add(round(this.border + colId*this.xDist));
          yVals.add(round(this.border + rowId*this.yDist));
        }

        for (int n=0; n < currentFired.size(); n++) {
          int n2;
          if (n < currentFired.size() -1 ) {
            n2 = n+1;
          } else {
            n2 = 0;
          }
          int x1 = (int) xVals.get(n);
          int y1 = (int) yVals.get(n);
          int x2 = (int) xVals.get(n2);
          int y2 = (int) yVals.get(n2);

          this.surface.line(x1, y1, x2, y2);
        }
      } else {
        println("Unknown plotmode", this.plotMode);
      }
    }
    this.surface.endDraw();
    image(this.surface, this.pos_x, this.pos_y);
  }

  void drawPoint(int neuron_id) {
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

int getCoord(int neuron_id, int idx) {
  JSONArray coords = (JSONArray) linear2grid.get(str(neuron_id));
  return coords.getInt(idx);
}
