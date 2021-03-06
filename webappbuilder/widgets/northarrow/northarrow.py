from webappbuilder.webbappwidget import WebAppWidget
import os
from PyQt4.QtGui import QIcon

class NorthArrow(WebAppWidget):

    def write(self, appdef, folder, app, progress):
        app.ol3controls.append("new ol.control.Rotate({autoHide: false})")

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(__file__), "north-arrow.png"))

    def description(self):
        return "North"