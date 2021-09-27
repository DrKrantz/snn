class NeuronNotes(OutputDevice):
    NAME = 'NeuronNotes'

    def __init__(self, midiport='SimpleSynth virtual input'):
        self.__noteRange = list(range(1, 127))
        self.__conversion = 7
        self.__midiport = midiport

        converter = Neuron2NoteConverter(
            conversion=self.__conversion,
            noteRange=self.__noteRange
        )
        super(NeuronNotes, self).__init__(
            DeviceStruct(midiport=self.__midiport),
            converter
        )


class Synth(OutputDevice):
    NAME = 'Synth'

    def __init__(self, midiport=''):
        self.__noteRange = list(range(1, 127))
        self.__conversion = 7
        self.__midiport = midiport

        deviceStruct = DeviceStruct(
            midiport=self.__midiport,
            maxNumSignals=4,
            updateInterval=5,
            velocity=80
        )
        converter = Neuron2NoteConverter(
            conversion=self.__conversion,
            noteRange=self.__noteRange
        )
        super(Synth, self).__init__(deviceStruct, converter)


class Piano(OutputDevice):
    NAME = 'Piano'

    def __init__(self, midiport=''):
        self.__noteRange = list(range(1, 96))
        self.__conversion = 7
        self.__midiport = midiport

        deviceStruct = DeviceStruct(
            midiport=self.__midiport,
            maxNumSignals=2,
            updateInterval=60,
            velocity=80
        )
        converter = Neuron2NoteConverter(
            conversion=self.__conversion,
            noteRange=self.__noteRange
        )
        super(Piano, self).__init__(deviceStruct, converter)


class Athmos(OutputDevice):
    NAME = 'Athmos'

    def __init__(self, midiport=''):
        self.__noteRange = list(range(1, 127))
        self.__conversion = 7
        self.__midiport = midiport

        deviceStruct = DeviceStruct(
            midiport=self.__midiport,
            maxNumSignals=4,
            updateInterval=5,
            velocity=80
        )
        converter = Neuron2NoteConverter(
            conversion=self.__conversion,
            noteRange=self.__noteRange
        )
        super(Athmos, self).__init__(deviceStruct, converter)


class Visuals(OutputDevice):
    NAME = 'Visuals'

    def __init__(self, midiport=''):
        self.__noteRange = list(range(1, 127))
        self.__conversion = 1
        self.__midiport = midiport

        deviceStruct = DeviceStruct(
            midiport=self.__midiport,
            maxNumSignals=1,
            updateInterval=10
        )
        converter = Neuron2NoteConverter(
            conversion=self.__conversion,
            noteRange=self.__noteRange
        )
        super(Visuals, self).__init__(deviceStruct, converter)


class DeviceStruct(dict):
    def __init__(self, midiport='SimpleSynth virtual input', maxNumSignals=None,
                 updateInterval=1, instrument=1, velocity=64, noteRange=list(range(1,127)),
                 neuron2NoteConversion=1):
        super(DeviceStruct, self).__init__()
        self['midiport'] = midiport
        self['maxNumSignals'] = maxNumSignals
        self['updateInterval'] = updateInterval
        self['instrument'] = instrument
        self['velocity'] = velocity
        self['noteRange'] = noteRange
        self['neuron2NoteConversion'] = neuron2NoteConversion


class DeviceFactory(object):
    NEURON_NOTES = 'SimpleSynth virtual input'
    OBJECT = 'MIDISPORT 2x2 Anniv Port BB'
    SYNTH = 'uMIDI/O22 Port 2'
    PIANO = 'MIDISPORT 2x2 Anniv Port 1'
    VISUALS = 'MIDISPORT 2x2 Anniv Port 1'
    ATHMOS = 'MIDISPORT 2x2 Anniv Port 2'#'uMIDI/O22 Port 2'

    def __init__(self):
        self.__name2DeviceStruct = {
            self.NEURON_NOTES: DeviceStruct(neuron2NoteConversion=7, noteRange = range(1,127)),

            self.OBJECT: DeviceStruct(name = self.OBJECT,
                                      maxNumSignals = 3,
                                      updateInterval = 45,
                                      velocity = 30),

            self.PIANO: DeviceStruct(name = self.PIANO,
                                     maxNumSignals = 2,
                                     updateInterval = 60,
                                     velocity = 80,
                                     noteRange = range(1,96)),

            self.SYNTH: DeviceStruct(name = self.SYNTH,
                                  maxNumSignals = 4,
                                  updateInterval = 5,
                                  velocity = 80),

            self.VISUALS: DeviceStruct(name = self.VISUALS,
                                      maxNumSignals = 1,
                                      updateInterval = 10,
                                      neuron2NoteConversion=1),

            self.ATHMOS: DeviceStruct(name = self.ATHMOS,
                                  maxNumSignals = 4,
                                  updateInterval = 5,
                                  velocity = 80),
            }

    def create(self, name):
        return OutputDevice(
            self.__name2DeviceStruct[name],
            Neuron2NoteConverter(
                noteRange=self.__name2DeviceStruct[name]['noteRange'],
                conversion=self.__name2DeviceStruct[name]['neuron2NoteConversion'],
                )
        )
