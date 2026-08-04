# coding=utf-8
from dragonfly.properties import ModelProperties, Room2DProperties
import dragonfly.writer.model as model_writer

from .properties.model import ModelTraceProperties
from .properties.room2d import Room2DTraceProperties
from .writer import model_to_trace700_matrix, model_to_trace700_csv, \
    model_to_trace700_workbook, model_to_trace700_gbxml, model_to_exp, \
    model_to_trace700_zip_bytes


# set a hidden trace attribute on each core geometry Property class to None
# define methods to produce trace property instances on each Property instance
ModelProperties._trace = None
Room2DProperties._trace = None

def model_trace_properties(self):
    if self._trace is None:
        self._trace = ModelTraceProperties(self.host)
    return self._trace


def room2d_trace_properties(self):
    if self._trace is None:
        self._trace = Room2DTraceProperties(self.host)
    return self._trace


# add trace property methods to the Properties classes
ModelProperties.trace = property(model_trace_properties)
Room2DProperties.trace = property(room2d_trace_properties)

# add writers to the honeybee-core modules
model_writer.trace700_matrix = model_to_trace700_matrix
model_writer.trace700_csv = model_to_trace700_csv
model_writer.trace700_workbook = model_to_trace700_workbook
model_writer.trace700_gbxml = model_to_trace700_gbxml
model_writer.trace700_exp = model_to_exp
model_writer.trace700_zip_bytes = model_to_trace700_zip_bytes
