from webappbuilder.webbappwidget import WebAppWidget
import os
from PyQt4.QtGui import QIcon

class SelectionTools(WebAppWidget):

    def write(self, appdef, folder, app, progress):
        app.tools.append('''React.createElement(Select, {toggleGroup: 'navigation', map:map})''')
        app.tools.append('''React.createElement(RaisedButton, {style: {margin: '10px 12px'}, label:'Navigation', onTouchTap:this._navigationFunc.bind(this)})''')

        self.addReactComponent(app, "Select")

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(__file__), "selection-tool.png"))

    def description(self):
        return "Selection"