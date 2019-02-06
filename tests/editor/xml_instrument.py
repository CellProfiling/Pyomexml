"""editting the info for the instrument."""
def edit_instrument(omexml):
    """add info of instrument to omexml"""
    omexml.instrument_count = 1
    instrument = omexml.instrument(0)
    instrument.ID = "Instrument:%d" % (0)
    instrument.microscope_count = 1
    edit_microscope(omexml)  # automatically inherit
    instrument.arc_count = 1
    edit_arc(omexml)
    instrument.detector_count = 1
    edit_detector(omexml)
    instrument.objective_count = 4
    edit_objective(omexml)
    instrument.filter_count = 8
    edit_filter(omexml)
    instrument.filterset_count = 4
    edit_fitlerset(omexml)
    instrument.dichroic_count = 4
    edit_dichroic(omexml)

#    return omexml

def edit_detector(omexml):
    detector0 = omexml.instrument(0).Detector(0)
    detector0.ID = "Detector:0"
    detector0.SerialNumber = "11533452"
    detector0.Type = "CMOS"
    detector0.Manufacturer = "Hamamatsu"
    detector0.Model = "Hamamatsu Flash 4.0 V3"
def edit_objective(omexml):
    objective0 = omexml.instrument(0).Objective(0)
    objective0.Immersion="Air"
    objective0.ID = "Objective:0"
    objective0.SerialNumber = "11506521"
    objective0.Correction = "Fluotar"
    objective0.LensNA = "0.32"

def edit_fitlerset(omexml):
    filterset0 = omexml.instrument(0).FilterSet(0)
    filterset0.ID = "FilterSet:DAPI"
    filterset0.Manufacturer = "Leica Microsystems"
    filterset0.SerialNumber = "11525304"
    filterset0.ExcitationFilterRef().ID = "ExcitationFilter:DAPI"
    filterset0.EmissionFilterRef().ID = "EmissionFilter:DAPI"
    filterset0.DichroicRef().ID = "Dichroic:DAPI"

    filterset1 = omexml.instrument(0).FilterSet(1)
    filterset1.ID = "FilterSet:FITC"
    filterset1.Manufacturer = "Leica Microsystems"
    filterset1.SerialNumber = "11525307"
    filterset1.ExcitationFilterRef().ID = "ExcitationFilter:FITC"
    filterset1.EmissionFilterRef().ID = "EmissionFilter:FITC"
    filterset1.DichroicRef().ID = "Dichroic:FITC"

    filterset2 = omexml.instrument(0).FilterSet(2)
    filterset2.ID = "FilterSet:RHOD"
    filterset2.Manufacturer = "Leica Microsystems"
    filterset2.SerialNumber = "11525308"
    filterset2.ExcitationFilterRef().ID = "ExcitationFilter:RHOD"
    filterset2.EmissionFilterRef().ID = "EmissionFilter:RHOD"
    filterset2.DichroicRef().ID = "Dichroic:RHOD"

    filterset3 = omexml.instrument(0).FilterSet(3)
    filterset3.ID = "FilterSet:Y5"
    filterset3.Manufacturer = "Leica Microsystems"
    filterset3.SerialNumber = "11525312"
    filterset3.ExcitationFilterRef().ID = "ExcitationFilter:Y5"
    filterset3.EmissionFilterRef().ID = "EmissionFilter:Y5"
    filterset3.DichroicRef().ID = "Dichroic:Y5"


def edit_dichroic(omexml):
    dichroic0 = omexml.instrument(0).Dichroic(0)
    dichroic0.ID = "Dichroic:DAPI"
    dichroic0.SerialNumber = "11525304"
    dichroic0.text = "400"

    dichroic1 = omexml.instrument(0).Dichroic(1)
    dichroic1.ID = "Dichroic:FITC"
    dichroic1.SerialNumber = "11525307"
    dichroic1.text = "505"

    dichroic2 = omexml.instrument(0).Dichroic(2)
    dichroic2.ID = "Dichroic:RHOD"
    dichroic2.SerialNumber = "11525308"
    dichroic2.text = "560"

    dichroic3 = omexml.instrument(0).Dichroic(3)
    dichroic3.ID = "Dichroic:Y5"
    dichroic3.SerialNumber = "11525312"
    dichroic3.text = "660"

def edit_filter(omexml):
    filter0 = omexml.instrument(0).Filter(0)
    filter0.ID = "ExcitationFilter:DAPI"
    filter0.SerialNumber = "11525304"
    filter0.Type = "BandPass"
    transmittancerange0 = filter0.TransmittanceRange(0)
    transmittancerange0.CutIn = "325"
    transmittancerange0.CutInUnit = "nm"
    transmittancerange0.CutOut = "375"
    transmittancerange0.CutOutUnit = "nm"
    filter1 = omexml.instrument(0).Filter(1)
    filter1.ID = "EmissionFilter:DAPI"
    filter1.SerialNumber = "11525304"
    filter1.Type = "BandPass"
    transmittancerange1 = filter1.TransmittanceRange(0)
    transmittancerange1.CutIn = "435"
    transmittancerange1.CutInUnit = "nm"
    transmittancerange1.CutOut = "485"
    transmittancerange1.CutOutUnit = "nm"

    filter2 = omexml.instrument(0).Filter(2)
    filter2.ID = "ExcitationFilter:FITC"
    filter2.SerialNumber = "11525307"
    filter2.Type = "BandPass"
    transmittancerange2 = filter2.TransmittanceRange(0)
    transmittancerange2.CutIn = "460"
    transmittancerange2.CutInUnit = "nm"
    transmittancerange2.CutOut = "500"
    transmittancerange2.CutOutUnit = "nm"
    filter3 = omexml.instrument(0).Filter(3)
    filter3.ID = "EmissionFilter:FITC"
    filter3.SerialNumber = "11525307"
    filter3.Type = "BandPass"
    transmittancerange3 = filter3.TransmittanceRange(0)
    transmittancerange3.CutIn = "512"
    transmittancerange3.CutInUnit = "nm"
    transmittancerange3.CutOut = "542"
    transmittancerange3.CutOutUnit = "nm"

    filter4 = omexml.instrument(0).Filter(4)
    filter4.ID = "ExcitationFilter:RHOD"
    filter4.SerialNumber = "11525308"
    filter4.Type = "BandPass"
    transmittancerange4 = filter4.TransmittanceRange(0)
    transmittancerange4.CutIn = "541"
    transmittancerange4.CutInUnit = "nm"
    transmittancerange4.CutOut = "551"
    transmittancerange4.CutOutUnit = "nm"
    filter5 = omexml.instrument(0).Filter(5)
    filter5.ID = "EmissionFilter:RHOD"
    filter5.SerialNumber = "11525308"
    filter5.Type = "BandPass"
    transmittancerange5 = filter5.TransmittanceRange(0)
    transmittancerange5.CutIn = "565"
    transmittancerange5.CutInUnit = "nm"
    transmittancerange5.CutOut = "605"
    transmittancerange5.CutOutUnit = "nm"

    filter6 = omexml.instrument(0).Filter(6)
    filter6.ID = "ExcitationFilter:Y5"
    filter6.SerialNumber = "11525312"
    filter6.Type = "BandPass"
    transmittancerange6 = filter6.TransmittanceRange(0)
    transmittancerange6.CutIn = "590"
    transmittancerange6.CutInUnit = "nm"
    transmittancerange6.CutOut = "650"
    transmittancerange6.CutOutUnit = "nm"
    filter7 = omexml.instrument(0).Filter(7)
    filter7.ID = "EmissionFilter:Y5"
    filter7.SerialNumber = "11525312"
    filter7.Type = "BandPass"
    transmittancerange7 = filter7.TransmittanceRange(0)
    transmittancerange7.CutIn = "663"
    transmittancerange7.CutInUnit = "nm"
    transmittancerange7.CutOut = "738"
    transmittancerange7.CutOutUnit = "nm"


def edit_arc(omexml):
    arc = omexml.instrument(0).Arc(0)
    arc.Manufacturer = "Leica Microsystems"
    arc.Type = "Hg"
    arc.ID = "Arc:0"
    arc.SerialNumber = "11504116"
    arc.Power = ""
    arc.PowerUnit = "mW"


def edit_microscope(omexml):
    microscope = omexml.instrument(0).Microscope(0)
    microscope.Manufacturer = "Leica Microsystems"
    microscope.Model = "DMI8"
    microscope.SerialNumber = "462130"
    microscope.LotNumber = "Unknown"
    microscope.Type = "Inverted"
