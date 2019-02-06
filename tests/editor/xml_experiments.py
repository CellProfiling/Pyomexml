"""Edit the experiments specifications"""

def edit_experiments(omexml):
    project = omexml.project()
    project.Name = "3D imaging"
    project.Description().text = "intro on the experiment"
    project.ID = "Project:0"
    project.ExperimenterRef().ID = "Experimenter:0"

    experiment = omexml.experiment()

    omexml.experimenter_count = 3
    for i in range(3):
        experimenter = omexml.experimenter(i)
        experimenter.ID = "Experimenter:%s" % str(i)
        experimenter.FirstName = "Martin Generation %s" % str(i)

    experimentergroup = omexml.experimentergroup()
    experimentergroup.Name = "CellProfiling"
    experimentergroup.ID = "ExperimenterGroup:0"
    experimentergroup.Description().text = "Cell Atlas of The Human Protein Atlas"
    experimentergroup.Leader().ID = "Experimenter:0"
