from PyQt6.QtCore import *

import traceback
import sys

# Klasa WorkerSignals zapewniająca współbieżność (używana przez Worker)
class WorkerSignals(QObject):
    result = pyqtSignal(object)
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    update_chat = pyqtSignal(list)  # Nowy sygnał do aktualizacji historii chatu

# Klasa Worker zapewniając współbieżność wykonywanych żądań 
class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.result.emit(result)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        finally:
            self.signals.finished.emit()
