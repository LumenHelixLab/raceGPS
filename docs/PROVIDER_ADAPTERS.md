# Provider Adapters

The app must not be hardwired to one map provider.

Adapters should expose:

- mount
- setCenter
- upsertPlayerMarker
- removePlayerMarker
- drawRoute
- searchPOI later
- geocode later

Default MVP adapter: mock map shell.

Future adapters:

- MapLibre/open data
- Mapbox
- CesiumJS
- Cesium for Unreal
- Licensed POI provider
