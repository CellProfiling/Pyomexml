"""editting the info for the image."""
import datetime

def xsd_now():
    '''Return the current time in xsd:dateTime format'''
    return datetime.datetime.now().isoformat()

def edit_image(omexml):
    '''add info of image to omexml'''
    omexml.image_count = 1
    image = omexml.image(0)
    image.ID = "Image:0"
    image.Name = "tubules.ome.tiff"
    image.Description().text = "what type is this image"
    image.AcquisitionDate().text = xsd_now()
    image.ExperimentRef().ID = "Experiment:0"
    image.ExperimenterRef().ID = "Experimenter:0"
    image.InstrumentRef().ID = "Instrument:0"
    image.pixels_count = 1
    edit_pixels(omexml)
    image.ROIRef().ID = "ROI:0"

def edit_pixels(omexml):
    pixels = omexml.image(0).Pixels(0)
    pixels.BigEndian = "True"
    pixels.DimensionOrder = "XYZCT"
    pixels.ID = "Pixels:0"
#    pixels.channel_count = 1
    edit_channel(pixels)
    edit_plane(pixels)
    tiffdata = pixels.TiffData()
    tiffdata.FirstC = "0"
    tiffdata.FirstT = "0"

def edit_plane(pixels):
    pixels.plane_count = 5
    for i in range(5):
        plane = pixels.Plane(i)
        plane.DeltaT = "500"

def edit_channel(pixels):
    channel = pixels.Channel()
    channel.AcquisitionMode = "Wide Field"
    channel.ContrastMethod = "Fluorescence"
    channel.ID = "Channel:0"
    channel.IlluminationType = "Epifluorescence"
#    channel.detectorsettings_count = 1
    edit_detectorsettings(channel)
    channel.LightSourceSettings().ID = "Arc:0"
    channel.LightSourceSettings().Wavelength = "Unknown"
    channel.FilterSetRef().ID = "FilterSet:DAPI"
    channel.LightPath().ExcitationFilterRef().ID = "ExcitationFilter:0"

def edit_detectorsettings(channel):
    detectorsettings = channel.DetectorSettings(0)
    detectorsettings.Binning = "2x2"
