from webappbuilder.webbappwidget import WebAppWidget
import os
from PyQt4.QtGui import QIcon

class LayersList(WebAppWidget):

    _parameters = {"tipLabel": "Layers",
                    "showOpacity": False,
                    "showZoomTo": False,
                    "showDownload": False,
                    "allowReordering": False,
                    "allowFiltering": True,
                    "expandOnHover": True,
                    "downloadFormat": ("GeoJSON", ("GeoJSON", "KML", "GPX"))}

    def write(self, appdef, folder, app, progress):
        def p(name):
            return str(self._parameters[name]).lower()
        app.panels.append('''React.createElement("div",{id: "layerlist"},
                                    React.createElement(LayerList, {showOpacity:%s, showDownload:%s,
                                        showGroupContent:true, showZoomTo:%s, allowReordering:%s,
                                        allowFiltering:%s, tipLabel:'%s', expandOnHover:%s,
                                        downloadFormat:'%s', map:map}))'''
                            % (p("showOpacity"),p("showDownload"), p("showZoomTo"),
                               p("allowReordering"), p("allowFiltering"), p("tipLabel"),
                               p("expandOnHover"), self._parameters["downloadFormat"][0]))
        self.addReactComponent(app, "LayerList")

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(__file__), "layer-list.png"))

    def description(self):
        return "Layers list"
