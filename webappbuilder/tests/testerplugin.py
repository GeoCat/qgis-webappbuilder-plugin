# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
import webbrowser

import settingstest
import widgetstest
import appdefvaliditytest
import symbologytest
import layerstest
from webappbuilder.tests.utils import (loadTestProject, createAppFromTestAppdef,
                                        loadTestProject, openWAB, closeWAB, testAppdef)

webAppFolder = None


def functionalTests():
    try:
        from qgistester.test import Test
        from qgistester.utils import layerFromName
    except:
        return []

    def _createWebApp(n):
        global webAppFolder
        webAppFolder = createAppFromTestAppdef(n)

    def _test(n):
        test = Test("Verify '%s' tutorial" % n)
        test.addStep("Setting up project", lambda: loadTestProject(n))
        test.addStep("Creating web app", lambda: _createWebApp(n))
        test.addStep("Verify web app in browser", prestep=lambda: webbrowser.open_new(
                    "file:///" + webAppFolder.replace("\\","/") + "/webapp/index_debug.html"))
        return test
    tests = [_test("bakeries"), _test("schools"), _test("fires")]

    unconfiguredBookmarksTest = Test("Verify bookmarks widget cannot be used if no bookmarks defined")
    unconfiguredBookmarksTest.addStep("Load project", lambda: loadTestProject())
    unconfiguredBookmarksTest.addStep("Open WAB", lambda: openWAB())
    unconfiguredBookmarksTest.addStep("Try to create an app with the bookmarks widget, without configuring it to add bookmarks.\n"
                         "Verify it shows a warning.")
    unconfiguredBookmarksTest.setCleanup(closeWAB)
    tests.append(unconfiguredBookmarksTest)


    unsupportedSymbologyTest = Test("Verify warning for unsupported symbology")
    unsupportedSymbologyTest.addStep("Load project", lambda: loadTestProject())
    unsupportedSymbologyTest.addStep("Open WAB", openWAB)
    unsupportedSymbologyTest.addStep("Click on 'Preview'. Verify a warning about unsupported symbology is shown.\n"
                         "Verify it shows a warning.")
    tests.append(unsupportedSymbologyTest)
    unsupportedSymbologyTest.setCleanup(closeWAB)

    wrongLogoTest = Test("Verify warning for wrong logo file")
    wrongLogoTest.addStep("Load project", lambda: loadTestProject())
    wrongLogoTest.addStep("Open WAB", openWAB)
    wrongLogoTest.addStep("Enter 'wrong' in the logo textbox and click on 'Preview'."
                                     "The logo texbox should get a yellow background.")
    wrongLogoTest.setCleanup(closeWAB)
    tests.append(wrongLogoTest)

    previewWithAllWidgetsTest = Test("Verify preview of an app with all tests")
    previewWithAllWidgetsTest.addStep("Load project", lambda: loadTestProject("layers"))
    appdef = testAppdef("allwidgets", False)
    previewWithAllWidgetsTest.addStep("Open WAB", lambda: openWAB(appdef))
    previewWithAllWidgetsTest.addStep("Click on 'Preview' and verify app is correctly shown and it works.")
    previewWithAllWidgetsTest.setCleanup(closeWAB)
    tests.append(previewWithAllWidgetsTest)

    return tests

def unitTests():
    _tests = []
    _tests.extend(settingstest.suite())
    _tests.extend(widgetstest.suite())
    _tests.extend(appdefvaliditytest.suite())
    _tests.extend(symbologytest.suite())
    _tests.extend(layerstest.suite())
    return _tests
