snn
===

# Vorbedingungen
_snn_ wird aus dem Terminal gestartet. Deswegen ist es notwendig, die grundlegendsten Terminal-Operationen zu kennen.
Die kurze Einführung hier https://phlow.de/magazin/terminal/datei-ordner-befehle/ sollte reichen.

Um ein python-script auszuführen (z.B. `script.py`) muss man `python script.py` ins Terminal eingeben und dann `Return` drücken. 
(man muss sich dazu natürlich in dem Verzeichnis befinden, in dem das script liegt...)

# Netzwerksimulator: `sensoryNetwork.py`
Der Netzwerksimulator von _snn_ wird gesteuert durch das python-script `sensoryNetwork.py`. 
Um die Simulation zu starten müssen zuerst die Konfigurationsdateien, die die Ein-und Ausgänge 
des Netzwerkes steuern, so angepasst werden, dass sie zum gewünschten setup passen.

## 1. Konfiguration
Die Konfiguration der Ausgänge erfolgt in zwei Schritten:
### 1.1. Konfiguration der Ausgangsgeräte: `outputs.json`
Das Verhalten eines Ausgangsgerätes kann durch mehrere Parameter kontrolliert werden. Zur Verfügung stehen:

| Parameter name  | default value  | Bedeutung     |
|-----------------|----------------|---------------| 
| max_num_signals |  None |               |
| update_interval |  1     |     |
| instrument      |   1    |  |
| velocity        |  64 | |
| min_note        | 1  |  |
| max_note        |  127  |  |
| conversion      | 1  | |
| force_off       | False  | |
| synchrony_limit |    1   | |

Die einzelnen Ausgangsgeräte werden in den Datei `config/outputs.json` spezifiziert. Hier können nach Belieben neue 
Geräte hinzugefügt werden, um neue Effekte zu erzielen. Wichtig dabei ist jedoch, die Formatierung der Datei beizubehalten!


### 1.2. Konfiguration der Verbindungen
Eine Übersicht der verfügbaren MIDI-ports erhält man durch Starten des Skripts `show_midi_ports.py`.

#### A. Ausgänge
Im zweiten Schritt muss festgelegt werden, welches Gerät an welchen MIDI-port angeschlossen sein soll. Dies wird in einer
weiteren `.json`-Datei festgehalten. Die Datei `config/output_wirings_local.json` z.B. sieht so aus

```commandline
{
  "neuron_notes": "IAC Driver Bus 1"
}
```
und besagt, dass nur ein Ausgangsgerät angeschlossen ist: `neuron_notes` am MIDI-port `"IAC Driver Bus 1"`. Für ein Beispiel
eines komplexeren Setups, betrachte die Datei `config/output_wirings.json`.


#### B. Eingänge
Auch die Eingänge werden per `json`-Datei konfiguriert. Will ich das sensorielle Objekt als Eingang anschliessen an den
port A vom MIDISPORT 2x2 anschliessen, so brauche ich eine Datei mit Inhalt (siehe `config/input_wiring.json`) 
```commandline
{
  "object": "MIDISPORT 2x2 Anniv A "
}
```
Für die Konfiguration mit keinem Eingangsgerät, betrachte die Datei  `config/input_wiring_local.json`.


#### WARNUNG
Aus mir nicht bekannten Gründen haben die Namen der MIDI-ports manchmal am Ende ein eigentlich überflüssiges Leerzeichen,
z.B. bei `"MIDISPORT 2x2 Anniv A "`. Wenn man dieses Leerzeichen in der Konfigurationsdatei weglässt, wird das Gerät NICHT gefunden!
Es ist also immer darauf zu achten, das Gerät in der `wiring`-Datei genau so zu bennenen, wie es von dem 
`show_midi_ports.py`-Skript ausgegeben wird.

## 2. Starten
Der Simulator wird gestartet durch das Skript `sensoryNetwork.py`. Ohne weitere Argumente startet die Simulation mit der 
Eingangskonfiguration `config/input_wirings_local.json` und der Ausgangskonfiguration `config/output_wirings_local.json`.
Sprich: es ist kein Eingangsgerät verbunden und alle Spike-Signale werden an den MIDI-port `"IAC Driver Bus 1"` gesendet.

Möchte man mit einer anderen Konfiguration starten, müssen beim Kommandoaufruf andere Konfigurationsdateien übergeben werden.
Die komplette Signatur des Kommandos ist:
```commandline
python sensoryNetwork.py -i INPUT_WIRING -o OUTPUT_WIRING
```
wobei `INPUT_WIRING` und `OUTPUT_WIRING` die Namen der Dateien sind, die die Verbindungen festlegen (siehe 1.2. Konfiguration der Verbindungen)


## 3. Stop
Die Simluation wird beendet durch GLEICHZEITIGES drücken der Tasten `CONTROL + C`.

# Parameter-Controller: `SimulationGui.py`


