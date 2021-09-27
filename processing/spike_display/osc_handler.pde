void oscEvent(OscMessage m) {
  if (m.checkAddrPattern("/display_spikes") == true) {
    println("receiving: ", m.arguments()[0]);
  }
}
