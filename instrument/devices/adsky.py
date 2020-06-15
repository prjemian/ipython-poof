
"""
area detector: ADSimDetector using IOC adsky
"""

__all__ = [
    'adsimdet',
    'paces',
    'shot',
    ]

from ..session_logs import logger
logger.info(__file__)

from bluesky import plans as bp
from bluesky import preprocessors as bpp

from ophyd import Component
from ophyd.areadetector import ADComponent
from ophyd.areadetector import EpicsSignalWithRBV
from ophyd.areadetector import HDF5Plugin
from ophyd.areadetector import ImagePlugin
from ophyd.areadetector import SimDetector
from ophyd.areadetector import SingleTrigger
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite


_ad_prefix = "adsky:"

DATABROKER_ROOT_PATH = "/tmp/"

# note: AD path MUST, must, MUST have trailing "/"!!!
#  ...and... start with the same path defined in root (above)

# path as seen by detector IOC
WRITE_HDF5_FILE_PATH = "/tmp/simdet/%Y/%m/%d/"
#!!! NOTE !!! This filesystem is on the IOC

# path as seen by bluesky data acquistion
READ_HDF5_FILE_PATH = "/tmp/docker_ioc/iocadsky/tmp/simdet/%Y/%m/%d/"


class MyHDF5Plugin(HDF5Plugin, FileStoreHDF5IterativeWrite):
    create_directory_depth = Component(EpicsSignalWithRBV, suffix="CreateDirectory")
    array_callbacks = Component(EpicsSignalWithRBV, suffix="ArrayCallbacks")

    pool_max_buffers = None
    
    def get_frames_per_point(self):
        return self.num_capture.get()

    def stage(self):
        super().stage()
        res_kwargs = {'frame_per_point': self.get_frames_per_point()}
        # res_kwargs = {'frame_per_point': self.num_capture.get()}
        self._generate_resource(res_kwargs)


class MySingleTriggerSimDetector(SingleTrigger, SimDetector):
    image = Component(ImagePlugin, suffix="image1:")
    hdf1 = ADComponent(
        MyHDF5Plugin,
        suffix='HDF1:', 
        root=DATABROKER_ROOT_PATH,
        write_path_template = WRITE_HDF5_FILE_PATH,
        read_path_template = READ_HDF5_FILE_PATH,
    )

adsimdet = MySingleTriggerSimDetector(_ad_prefix, name='adsimdet')
adsimdet.wait_for_connection()
adsimdet.stage_sigs["cam.num_images"] = 1
adsimdet.stage_sigs["cam.acquire_time"] = 0.01
adsimdet.stage_sigs["cam.acquire_period"] = 0.02
adsimdet.hdf1.stage_sigs["num_capture"] = 1

adsimdet.read_attrs.append("hdf1")
if adsimdet.hdf1.create_directory_depth.get() == 0:
    # probably not set, so let's set it now to some default
    adsimdet.hdf1.create_directory_depth.put(-5)

enabled = adsimdet.hdf1.enable.get()
adsimdet.hdf1.warmup()
adsimdet.hdf1.enable.put(enabled)


def shot(images=1, exposures=1, num=1, md={}):
    adsimdet.stage_sigs["cam.num_images"] = images
    adsimdet.stage_sigs["cam.num_exposures"] = exposures
    adsimdet.hdf1.stage_sigs["num_capture"] = exposures * images
    _md = dict(
        num_counts=num,
        num_images=images,
        num_exposures=exposures,
    )
    _md.update(md)

    # logger.info("new metadata: %s", _md)
    yield from bp.count([adsimdet], num=num, md=_md)
    print(adsimdet.hdf1.full_file_name.get())


def paces(title=None, md={}):
    title=title or "area detector acquisition"
    _md = dict(title=title)
    _md.update(md)
    for num in (2, 1):
        for images in (2, 1):
            for exposures in (2, 1):
                yield from shot(images, exposures, num, md=_md)

"""
RE(paces(), subtitle=""with HDF5 plugin"")

produced these run IDs:

('c9ff4482-cf96-4853-97f4-4076fe072b28',
 '5095a0d1-2237-425e-96cd-0b8254e2512e',
 'cae72c86-445f-4a29-bd6e-be4830be1750',
 'd1a7e3aa-bb41-4d84-81ae-96ddcabcd16c',
 '748a8f1e-b38f-4d63-89e9-2d27cf0dbff9',
 '8882024d-273c-4d8e-a605-72069099c302',
 'dc989fe0-82c7-4891-a5bf-dc0cac38b787',
 'f116f058-7662-437d-a0c9-6d3a4828f245')

In [10]: listruns(keys=["title", "subtitle"], num=40)
========= ========================== ======= ======= ==================================== ========================= ================
short_uid date/time                  exit    scan_id command                              title                     subtitle
========= ========================== ======= ======= ==================================== ========================= ================
f116f05   2020-06-15 10:18:10.967403 success 523     count(detectors=['adsimdet'], num=1) area detector acquisition with HDF5 plugin
dc989fe   2020-06-15 10:18:10.844898 success 522     count(detectors=['adsimdet'], num=1) area detector acquisition with HDF5 plugin
8882024   2020-06-15 10:18:10.755637 success 521     count(detectors=['adsimdet'], num=1) area detector acquisition with HDF5 plugin
748a8f1   2020-06-15 10:18:10.650733 success 520     count(detectors=['adsimdet'], num=1) area detector acquisition with HDF5 plugin
d1a7e3a   2020-06-15 10:18:10.551688 success 519     count(detectors=['adsimdet'], num=2) area detector acquisition with HDF5 plugin
cae72c8   2020-06-15 10:18:10.462899 success 518     count(detectors=['adsimdet'], num=2) area detector acquisition with HDF5 plugin
5095a0d   2020-06-15 10:18:10.330561 success 517     count(detectors=['adsimdet'], num=2) area detector acquisition with HDF5 plugin
c9ff448   2020-06-15 10:18:10.149116 success 516     count(detectors=['adsimdet'], num=2) area detector acquisition with HDF5 plugin
098d5fc   2020-06-15 10:16:31.666679 success 515     count(detectors=['adsimdet'], num=1) area detector acquisition
00adc22   2020-06-15 10:16:31.579642 success 514     count(detectors=['adsimdet'], num=1) area detector acquisition
6866f00   2020-06-15 10:16:31.462799 success 513     count(detectors=['adsimdet'], num=1) area detector acquisition
ca66eb8   2020-06-15 10:16:31.301427 success 512     count(detectors=['adsimdet'], num=1) area detector acquisition
d232652   2020-06-15 10:16:31.200080 success 511     count(detectors=['adsimdet'], num=2) area detector acquisition
33c93da   2020-06-15 10:16:31.102913 success 510     count(detectors=['adsimdet'], num=2) area detector acquisition
32656a7   2020-06-15 10:16:30.959172 success 509     count(detectors=['adsimdet'], num=2) area detector acquisition
fe9c05b   2020-06-15 10:16:30.633129 success 508     count(detectors=['adsimdet'], num=2) area detector acquisition
9131d2b   2020-06-15 10:07:11.510882 success 507     count(detectors=['adsimdet'], num=1) area detector acquisition
60a77b9   2020-06-15 10:07:11.487699 success 506     count(detectors=['adsimdet'], num=1) area detector acquisition
b9b2785   2020-06-15 10:07:11.458462 success 505     count(detectors=['adsimdet'], num=1) area detector acquisition
74c6348   2020-06-15 10:07:11.427158 success 504     count(detectors=['adsimdet'], num=1) area detector acquisition
f94ee4d   2020-06-15 10:07:11.352479 success 503     count(detectors=['adsimdet'], num=2) area detector acquisition
1d5a154   2020-06-15 10:07:11.321396 success 502     count(detectors=['adsimdet'], num=2) area detector acquisition
81cc6ee   2020-06-15 10:07:11.258743 success 501     count(detectors=['adsimdet'], num=2) area detector acquisition
989af1b   2020-06-15 10:07:11.187831 success 500     count(detectors=['adsimdet'], num=2) area detector acquisition
cc48ac3   2020-06-15 10:05:56.864013 success 499     count(detectors=['adsimdet'], num=1) area detector acquisition
4109ab9   2020-06-15 10:05:56.840034 success 498     count(detectors=['adsimdet'], num=1) area detector acquisition
b52b278   2020-06-15 10:05:56.810695 success 497     count(detectors=['adsimdet'], num=1) area detector acquisition
928a994   2020-06-15 10:05:56.761995 success 496     count(detectors=['adsimdet'], num=1) area detector acquisition
39fd649   2020-06-15 10:05:56.731592 success 495     count(detectors=['adsimdet'], num=2) area detector acquisition
6324c9d   2020-06-15 10:05:56.697515 success 494     count(detectors=['adsimdet'], num=2) area detector acquisition
065aa5b   2020-06-15 10:05:56.625276 success 493     count(detectors=['adsimdet'], num=2) area detector acquisition
3c42786   2020-06-15 10:05:56.575641 success 492     count(detectors=['adsimdet'], num=2) area detector acquisition
6e3c2c8   2020-06-15 10:05:35.595691 success 491     count(detectors=['adsimdet'], num=1)
ce7b9ef   2020-06-15 10:05:35.571459 success 490     count(detectors=['adsimdet'], num=1)
4bbf20b   2020-06-15 10:05:35.521658 success 489     count(detectors=['adsimdet'], num=1)
9d6a445   2020-06-15 10:05:35.492893 success 488     count(detectors=['adsimdet'], num=1)
d02afb3   2020-06-15 10:05:35.458769 success 487     count(detectors=['adsimdet'], num=2)
39b3a4a   2020-06-15 10:05:35.332236 success 486     count(detectors=['adsimdet'], num=2)
844f6b9   2020-06-15 10:05:35.288693 success 485     count(detectors=['adsimdet'], num=2)
1b7ccca   2020-06-15 10:05:35.239403 success 484     count(detectors=['adsimdet'], num=2)
========= ========================== ======= ======= ==================================== ========================= ================

"""