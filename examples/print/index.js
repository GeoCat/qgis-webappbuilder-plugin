var container = document.getElementById('popup');
var content = document.getElementById('popup-content');
var closer = document.getElementById('popup-closer');
closer.onclick = function() {
    container.style.display = 'none';
    closer.blur();
    return false;
};

var overlayPopup = new ol.Overlay({
    element: container
});

var view = new ol.View({
    center: [0, 0],
    zoom: 7,
    maxZoom: 32,
    minZoom: 1,
    projection: 'EPSG:3857'
});

var pointZoom = 16;

var map = new ol.Map({
    controls: [
        new ol.control.ScaleLine({
            "minWidth": 64,
            "units": "metric"
        }),
        new ol.control.LayerSwitcher({
            "showZoomTo": false,
            "allowFiltering": true,
            "allowReordering": false,
            "showDownload": false,
            "showOpacity": false,
            "tipLabel": "Layers"
        }),
        new ol.control.Zoom({
            "zoomInTipLabel": "Zoom in",
            "zoomOutLabel": "-",
            "zoomOutTipLabel": "Zoom out",
            "duration": 250,
            "zoomInLabel": "+",
            "delta": 1.2
        })
    ],
    target: document.getElementById('map'),
    renderer: 'canvas',
    overlays: [overlayPopup],
    layers: layersList,
    view: view
});

var originalExtent = [-18259309.351575, 8868377.155791, -16357531.492588, 10059892.592315];
map.getView().fit(originalExtent, map.getSize());

var currentInteraction;



popupLayers = [``, ``, ``, ``, ``, `<b>cat</b>: [cat]<br><b>F_CODEDESC</b>: [F_CODEDESC]<br><b>F_CODE</b>: [F_CODE]<br><b>TYPE</b>: [TYPE]`, ``];

var popupEventTriggered = function(evt) {
    var pixel = map.getEventPixel(evt.originalEvent);
    var coord = evt.coordinate;
    var popupTexts = [];
    var currentFeature;
    var allLayers = getAllNonBaseLayers();
    map.forEachFeatureAtPixel(pixel, function(feature, layer) {
        feature = decluster(feature);
        if (feature) {
            popupDef = popupLayers[allLayers.indexOf(layer)];
            if (popupDef) {
                var featureKeys = feature.getKeys();
                for (var i = 0; i < featureKeys.length; i++) {
                    if (featureKeys[i] != 'geometry') {
                        var value = feature.get(featureKeys[i]);
                        if (value) {
                            popupDef = popupDef.split("[" + featureKeys[i] + "]").join(
                                String(feature.get(featureKeys[i])))
                        } else {
                            popupDef = popupDef.split("[" + featureKeys[i] + "]").join("NULL")
                        }
                    }
                }
                popupTexts.push(popupDef);
            }
        }
    });

    var fetchData = function(cb) {
        var geojsonFormat = new ol.format.GeoJSON();
        var len = allLayers.length;
        var finishedQueries = 0;
        for (var i = 0; i < len; i++) {
            var layer = allLayers[i];
            if (layer.getSource() instanceof ol.source.TileWMS) {
                var popupDef = popupLayers[allLayers.indexOf(layer)];
                if (popupDef == "#AllAttributes") {
                    var url = layer.getSource().getGetFeatureInfoUrl(
                        evt.coordinate,
                        map.getView().getResolution(),
                        map.getView().getProjection(), {
                            'INFO_FORMAT': 'text/plain'
                        }
                    );
                    $.ajax({
                        type: 'GET',
                        url: url,
                        success: function(data) {
                            popupTexts.push(data);
                            finishedQueries++;
                            if (len == finishedQueries) {
                                cb();
                            }
                        }
                    });
                } else if (popupDef !== "") {
                    var url = layer.getSource().getGetFeatureInfoUrl(
                        evt.coordinate,
                        map.getView().getResolution(),
                        map.getView().getProjection(), {
                            'INFO_FORMAT': 'application/json'
                        }
                    );
                    $.ajax({
                        url: url,
                        success: function(data) {
                            var features = geojsonFormat.readFeatures(data);
                            for (var f = 0; f < features.length; f++) {
                                var feature = features[f];
                                var values = feature.getProperties();
                                for (var key in values) {
                                    if (key != 'geometry') {
                                        var value = values[key];
                                        if (value) {
                                            popupDef = popupDef.split("[" + key + "]").join(
                                                String(value));
                                        } else {
                                            popupDef = popupDef.split("[" + key + "]").join("NULL");
                                        }
                                    }
                                }
                                popupTexts.push(popupDef);
                                finishedQueries++;
                            }
                        }
                    });
                }
            } else {
                finishedQueries++;
            }
        }
        cb();
    }

    fetchData(function() {
        if (popupTexts.length) {
            overlayPopup.setPosition(coord);
            content.innerHTML = popupTexts.join("<hr>");
            container.style.display = 'block';
        } else {
            container.style.display = 'none';
            closer.blur();
        }
    });

};

map.on('singleclick', function(evt) {
    popupEventTriggered(evt);
});