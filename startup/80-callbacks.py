print(__file__)

# custom callbacks
from APS_BlueSky_tools.callbacks import DocumentCollectorCallback
from APS_BlueSky_tools.filewriters import SpecWriterCallback


doc_collector = DocumentCollectorCallback()
callback_db['doc_collector'] = RE.subscribe(doc_collector.receiver)

specwriter = SpecWriterCallback()
callback_db['specwriter'] = RE.subscribe(specwriter.receiver)

now = datetime.now()
sfname = datetime.strftime(now, "/tmp/%Y%m%d-%H%M%S")+".dat"
print("writing data to SPEC file: ", sfname)
specwriter.newfile(sfname)
