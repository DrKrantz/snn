void oscEvent(OscMessage m) {
  //println("message addr pattern"  + m.addrPattern());
  if (m.checkAddrPattern(SPIKE_DISPLAY_ADDRESS) == true) {
    JSONObject newData = parseJSONObject((String) m.arguments()[0]);
    JSONArray fired = (JSONArray) newData.get("fired");
    spikeSurface.set_fired(fired);
  } else {
    println("Unknown address  " + m.addrPattern());
  }
}
