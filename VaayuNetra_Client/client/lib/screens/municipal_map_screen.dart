import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

class MunicipalMapScreen extends StatefulWidget {
  const MunicipalMapScreen({super.key});

  @override
  State<MunicipalMapScreen> createState() => _MunicipalMapScreenState();
}

class _MunicipalMapScreenState extends State<MunicipalMapScreen> {
  final ApiService _apiService = ApiService();
  final MapController _mapController = MapController();

  bool _isLoading = true;
  String? _errorMessage;
  List<Marker> _markers = [];
  List<Polygon> _polygons = [];
  Map<String, dynamic>? _selectedFeatureProperties;

  @override
  void initState() {
    super.initState();
    _fetchMunicipalIncidents();
  }

  Future<void> _fetchMunicipalIncidents() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final geojson = await _apiService.getMunicipalIncidents();
      _parseGeoJson(geojson);
      setState(() {
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  void _parseGeoJson(Map<String, dynamic> geojson) {
    final features = geojson['features'] as List<dynamic>? ?? [];
    final markers = <Marker>[];
    final polygons = <Polygon>[];

    for (final feature in features) {
      final featMap = feature as Map<String, dynamic>;
      final geometry = featMap['geometry'] as Map<String, dynamic>? ?? {};
      final properties = featMap['properties'] as Map<String, dynamic>? ?? {};
      final type = geometry['type'] as String? ?? '';

      if (type == 'Point') {
        final coords = geometry['coordinates'] as List<dynamic>? ?? [];
        if (coords.length >= 2) {
          final lon = (coords[0] as num).toDouble();
          final lat = (coords[1] as num).toDouble();

          markers.add(
            Marker(
              point: LatLng(lat, lon),
              width: 44,
              height: 44,
              child: GestureDetector(
                onTap: () {
                  setState(() {
                    _selectedFeatureProperties = properties;
                  });
                },
                child: Container(
                  decoration: BoxDecoration(
                    color: AppTheme.hazardCoral,
                    shape: BoxShape.circle,
                    border: Border.all(color: Colors.white, width: 2),
                    boxShadow: [
                      BoxShadow(
                        color: AppTheme.hazardCoral.withValues(alpha: 0.5),
                        blurRadius: 10,
                        spreadRadius: 2,
                      ),
                    ],
                  ),
                  child: const Icon(
                    Icons.local_fire_department_rounded,
                    color: Color(0xFF1B1438),
                    size: 22,
                  ),
                ),
              ),
            ),
          );
        }
      } else if (type == 'Polygon') {
        final rings = geometry['coordinates'] as List<dynamic>? ?? [];
        if (rings.isNotEmpty) {
          final exteriorRing = rings[0] as List<dynamic>? ?? [];
          final polyPoints = <LatLng>[];

          for (final coord in exteriorRing) {
            final pt = coord as List<dynamic>;
            if (pt.length >= 2) {
              final lon = (pt[0] as num).toDouble();
              final lat = (pt[1] as num).toDouble();
              polyPoints.add(LatLng(lat, lon));
            }
          }

          if (polyPoints.length >= 3) {
            final priority = properties['alert_priority'] as String? ?? 'MODERATE';
            final polyColor = priority == 'CRITICAL'
                ? AppTheme.hazardCoral
                : (priority == 'HIGH' ? const Color(0xFFFBBF24) : AppTheme.primaryAccent);

            polygons.add(
              Polygon(
                points: polyPoints,
                color: polyColor.withValues(alpha: 0.28),
                borderColor: polyColor,
                borderStrokeWidth: 2.0,
              ),
            );
          }
        }
      }
    }

    _markers = markers;
    _polygons = polygons;
  }

  Future<void> _injectSimulationSpike() async {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          backgroundColor: Color(0xFF221A44),
          content: Text(
            'Simulating stubble fire spike across all sockets...',
            style: TextStyle(color: AppTheme.textHeader),
          ),
        ),
      );
    }

    try {
      await _apiService.simulateSpike(
        lat: 28.6139,
        lon: 77.2090,
        category: 'agricultural_stubble_burning',
      );
      await _fetchMunicipalIncidents();
      _mapController.move(const LatLng(28.6139, 77.2090), 11.0);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            backgroundColor: Color(0xFF221A44),
            content: Text('Simulation error: $e', style: const TextStyle(color: AppTheme.hazardCoral)),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(gradient: AppTheme.backgroundGradient),
      child: Scaffold(
        backgroundColor: Colors.transparent,
        appBar: AppBar(
          backgroundColor: Colors.transparent,
          elevation: 0,
          title: const Row(
            children: [
              Icon(Icons.map_rounded, color: AppTheme.primaryAccent, size: 20),
              SizedBox(width: 10),
              Text(
                'Municipal Dispersion Command',
                style: TextStyle(
                  fontSize: 16.5,
                  fontWeight: FontWeight.w600,
                  color: AppTheme.textHeader,
                  letterSpacing: 0.2,
                ),
              ),
            ],
          ),
          actions: [
            IconButton(
              icon: const Icon(Icons.refresh_rounded, color: AppTheme.textMuted),
              onPressed: _fetchMunicipalIncidents,
            ),
          ],
        ),
        floatingActionButtonLocation: FloatingActionButtonLocation.miniCenterFloat,
        floatingActionButton: Padding(
          padding: const EdgeInsets.only(bottom: 70),
          child: Container(
            height: 44,
            decoration: BoxDecoration(
              gradient: AppTheme.buttonGradient,
              borderRadius: BorderRadius.circular(30),
              boxShadow: [
                BoxShadow(
                  color: AppTheme.primaryAccent.withValues(alpha: 0.3),
                  blurRadius: 16,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                borderRadius: BorderRadius.circular(30),
                onTap: _injectSimulationSpike,
                child: const Padding(
                  padding: EdgeInsets.symmetric(horizontal: 18),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.bolt_rounded, color: AppTheme.buttonTextColor, size: 18),
                      SizedBox(width: 6),
                      Text(
                        'Pitch Demo Spike',
                        style: TextStyle(
                          color: AppTheme.buttonTextColor,
                          fontWeight: FontWeight.w700,
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
        body: Stack(
          children: [
            // FlutterMap Canvas
            FlutterMap(
              mapController: _mapController,
              options: const MapOptions(
                initialCenter: LatLng(28.6139, 77.2090),
                initialZoom: 10.5,
                minZoom: 4,
                maxZoom: 18,
              ),
              children: [
                TileLayer(
                  urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                  userAgentPackageName: 'com.vaayunetra.client',
                ),
                PolygonLayer(polygons: _polygons),
                MarkerLayer(markers: _markers),
              ],
            ),

            // Loading Overlay
            if (_isLoading)
              Positioned(
                top: 14,
                left: 16,
                right: 16,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1C1635).withValues(alpha: 0.92),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: const Color(0xFF5A4982).withValues(alpha: 0.4)),
                  ),
                  child: const Row(
                    children: [
                      SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(color: AppTheme.primaryAccent, strokeWidth: 2),
                      ),
                      SizedBox(width: 12),
                      Text(
                        'Loading dispersion polygons & incidents...',
                        style: TextStyle(color: AppTheme.textHeader, fontSize: 12),
                      ),
                    ],
                  ),
                ),
              ),

            // Error Overlay
            if (_errorMessage != null)
              Positioned(
                top: 14,
                left: 16,
                right: 16,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                  decoration: BoxDecoration(
                    color: AppTheme.hazardCoral.withValues(alpha: 0.95),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    _errorMessage!,
                    style: const TextStyle(color: Color(0xFF1B1438), fontSize: 12, fontWeight: FontWeight.w600),
                  ),
                ),
              ),

            // Map Legend
            Positioned(
              bottom: 125,
              left: 16,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                decoration: BoxDecoration(
                  color: const Color(0xFF1C1635).withValues(alpha: 0.88),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFF5A4982).withValues(alpha: 0.4)),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.3),
                      blurRadius: 14,
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Text(
                      'DISPERSION LEGEND',
                      style: TextStyle(
                        color: AppTheme.textMuted,
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 0.5,
                      ),
                    ),
                    const SizedBox(height: 6),
                    _buildLegendItem(AppTheme.hazardCoral, 'Incident Origin (Fire/Smoke)'),
                    const SizedBox(height: 4),
                    _buildLegendItem(const Color(0xFFFBBF24).withValues(alpha: 0.8), '30° Downwind Plume Cone'),
                  ],
                ),
              ),
            ),

            // Inspector Bottom Sheet
            if (_selectedFeatureProperties != null)
              Positioned(
                bottom: 125,
                left: 16,
                right: 16,
                child: Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: const Color(0xFF221A44).withValues(alpha: 0.95),
                    borderRadius: BorderRadius.circular(22),
                    border: Border.all(color: AppTheme.primaryAccent.withValues(alpha: 0.5), width: 1.2),
                    boxShadow: [
                      BoxShadow(color: Colors.black.withValues(alpha: 0.45), blurRadius: 18),
                    ],
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            _selectedFeatureProperties!['ticket_id']?.toString() ?? 'VN-INCIDENT',
                            style: const TextStyle(color: AppTheme.primaryAccent, fontWeight: FontWeight.bold, fontSize: 15),
                          ),
                          IconButton(
                            padding: EdgeInsets.zero,
                            constraints: const BoxConstraints(),
                            icon: const Icon(Icons.close_rounded, color: AppTheme.textMuted, size: 20),
                            onPressed: () => setState(() => _selectedFeatureProperties = null),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Category: ${_selectedFeatureProperties!['category'] ?? 'N/A'}',
                        style: const TextStyle(color: AppTheme.textHeader, fontSize: 13),
                      ),
                      const SizedBox(height: 3),
                      Text(
                        'Wind: ${_selectedFeatureProperties!['wind_speed_kmh'] ?? '--'} km/h @ ${_selectedFeatureProperties!['wind_direction_deg'] ?? '--'}°',
                        style: const TextStyle(color: AppTheme.textMuted, fontSize: 12),
                      ),
                      const SizedBox(height: 3),
                      Text(
                        'Vulnerability Score: ${_selectedFeatureProperties!['vulnerability_score'] ?? '--'}/100',
                        style: const TextStyle(color: AppTheme.safeMint, fontSize: 12, fontWeight: FontWeight.w600),
                      ),
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildLegendItem(Color color, String label) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 10,
          height: 10,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 8),
        Text(label, style: const TextStyle(color: AppTheme.textHeader, fontSize: 11)),
      ],
    );
  }
}
