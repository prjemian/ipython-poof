print(__file__)

# custom callbacks
from APS_BlueSky_tools.callbacks import DocumentCollectorCallback
from APS_BlueSky_tools.filewriters import SpecWriterCallback


doc_collector = DocumentCollectorCallback()
callback_db['doc_collector'] = RE.subscribe(doc_collector.receiver)

specwriter = SpecWriterCallback()
callback_db['specwriter'] = RE.subscribe(specwriter.receiver)
# make the default SPEC data file in /tmp/yyyymmdd-hhmmss.dat
specwriter.newfile(os.path.join("/tmp", specwriter.spec_filename))
print("writing data to SPEC file: ", specwriter.spec_filename)
