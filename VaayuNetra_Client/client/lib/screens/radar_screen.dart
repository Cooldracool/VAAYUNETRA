import 'dart:async';
import 'dart:convert';
import 'dart:math' as math;
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;
import '../models/ticket.dart';
import '../services/api_service.dart';

class RadarScreen extends StatefulWidget {
  const RadarScreen({super.key});

  @override
  State<RadarScreen> createState() => _RadarScreenState();
}

class _RadarScreenState extends State<RadarScreen> with SingleTickerProviderStateMixin {
  final ApiService _apiService = ApiService();
  double _currentLat = 18.5204; // Default Pune Central Corridor
  double _currentLon = 73.8567;

  // Location state variables as required
  bool isLocating = true;
  bool locationFailed = false;
  String locationName = "Detecting your corridor...";

  bool _isLoading = false;
  String? _statusNotice;

  // Spatial plume corridor alert state
  Timer? _alertTimer;
  bool _insideHazardZone = true;
  String _hazardMessage =
      'Hazard Zone: You are inside the downwind smoke dispersion path (~1.2 km from reported fire).';

  // Initialize immediately with safe default mock data so screen is NEVER empty
  FeedResponse _feedData = FeedResponse.mockDefault(location: 'Pune Central Corridor');

  // Subtle background star twinkling animation
  late AnimationController _starController;

  @override
  void initState() {
    super.initState();
    _starController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 4),
    )..repeat();

    fetchHyperlocalData();

    // Periodic check (every 5 seconds) to /api/v1/alerts/check?lat={lat}&lon={lon}
    _alertTimer = Timer.periodic(const Duration(seconds: 5), (_) {
      _checkAlerts();
    });
  }

  @override
  void dispose() {
    _alertTimer?.cancel();
    _starController.dispose();
    super.dispose();
  }

  Future<void> fetchHyperlocalData() async {
    setState(() {
      isLocating = true;
      locationFailed = false;
      _isLoading = true;
    });

    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        throw Exception('Location service disabled');
      }

      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }
      if (permission == LocationPermission.denied ||
          permission == LocationPermission.deniedForever) {
        throw Exception('Location permission denied');
      }

      // ignore: deprecated_member_use
      final pos = await Geolocator.getCurrentPosition(
        // ignore: deprecated_member_use
        desiredAccuracy: LocationAccuracy.medium,
        // ignore: deprecated_member_use
        timeLimit: const Duration(seconds: 20),
      );

      _currentLat = pos.latitude;
      _currentLon = pos.longitude;

      // On success: Make the reverse geocode call to Nominatim
      String name = 'Local Zone';
      try {
        final uri = Uri.parse(
          'https://nominatim.openstreetmap.org/reverse?lat=${pos.latitude}&lon=${pos.longitude}&format=json',
        );
        final response = await http.get(
          uri,
          headers: {'User-Agent': 'VaayuNetraDemo/1.0'},
        ).timeout(const Duration(seconds: 8));

        if (response.statusCode == 200) {
          final data = jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
          final addr = data['address'] as Map<String, dynamic>? ?? {};
          name = addr['suburb'] ?? addr['neighbourhood'] ?? addr['city'] ?? addr['town'] ?? 'Local Zone';
        }
      } catch (_) {
        // Fall back to Local Zone on network issue
      }

      if (mounted) {
        setState(() {
          locationName = "$name Corridor";
          isLocating = false;
          locationFailed = false;
        });
      }

      // Also pass those resolved coordinates to /api/v1/feed?lat=${pos.latitude}&lon=${pos.longitude}
      // and /api/v1/alerts/check?lat=${pos.latitude}&lon=${pos.longitude}
      await _fetchFeed(pos.latitude, pos.longitude);
      await _checkAlerts(pos.latitude, pos.longitude);
    } catch (_) {
      if (mounted) {
        setState(() {
          isLocating = false;
          locationFailed = true;
          locationName = "Location unavailable";
          _isLoading = false;
        });
      }
      // Keep feed active with fallback data so UI remains interactive
      await _fetchFeed();
    }
  }

  Future<void> _fetchFeed([double? lat, double? lon]) async {
    final targetLat = lat ?? _currentLat;
    final targetLon = lon ?? _currentLon;
    setState(() {
      _isLoading = true;
      _statusNotice = null;
    });

    try {
      final feed = await _apiService.getFeed(targetLat, targetLon, locationName);
      if (mounted) {
        setState(() {
          _feedData = feed;
          if (feed.location.isNotEmpty &&
              feed.location != 'Patna West Corridor' &&
              (locationName == 'Detecting your corridor...' || locationName == 'Location unavailable')) {
            locationName = feed.location;
          }
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _feedData = FeedResponse.mockDefault(
            location: (locationName != 'Detecting your corridor...' && locationName != 'Location unavailable')
                ? locationName
                : 'Pune Central Corridor',
            lat: targetLat,
            lon: targetLon,
          );
          _isLoading = false;
          _statusNotice = 'Running in offline cached telemetry mode';
        });
      }
    }
  }

  Future<void> _checkAlerts([double? lat, double? lon]) async {
    final targetLat = lat ?? _currentLat;
    final targetLon = lon ?? _currentLon;
    try {
      final alert = await _apiService.checkAlerts(targetLat, targetLon);
      if (mounted) {
        setState(() {
          _insideHazardZone = alert['inside_hazard_zone'] == true;
          if (alert['message'] != null && (alert['message'] as String).isNotEmpty) {
            _hazardMessage = alert['message'] as String;
          }
        });
      }
    } catch (_) {
      // Retain active hazard status if offline
    }
  }

  void _showGatewayDialog() {
    final controller = TextEditingController(text: ApiService.baseUrl);
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF221A44),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(24),
          side: BorderSide(color: Colors.white.withValues(alpha: 0.1)),
        ),
        title: const Text(
          'Telemetry Gateway',
          style: TextStyle(color: Colors.white, fontSize: 17, fontWeight: FontWeight.w600),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Set host URL (use 10.0.2.2:8000 for Android emulator, 127.0.0.1:8000 for Web/Desktop, or your LAN IP).',
              style: TextStyle(color: Color(0xFFAFA3CE), fontSize: 12.5),
            ),
            const SizedBox(height: 14),
            TextField(
              controller: controller,
              style: const TextStyle(color: Colors.white, fontSize: 13.5),
              decoration: InputDecoration(
                filled: true,
                fillColor: const Color(0xFF171233),
                contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(14),
                  borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.1)),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(14),
                  borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.1)),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(14),
                  borderSide: const BorderSide(color: Color(0xFFD3C1F5)),
                ),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel', style: TextStyle(color: Color(0xFFAFA3CE))),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFD3C1F5),
              foregroundColor: const Color(0xFF1B1438),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
            ),
            onPressed: () {
              ApiService.customBaseUrl = controller.text.trim();
              Navigator.pop(ctx);
              _fetchFeed();
            },
            child: const Text('Save & Connect', style: TextStyle(fontWeight: FontWeight.w700)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF131028),
      body: Stack(
        children: [
          // 1. Cosmic Matte Night Gradient Background
          Container(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  Color(0xFF131028),
                  Color(0xFF201842),
                  Color(0xFF161130),
                ],
              ),
            ),
          ),

          // 2. Subtle Twinkling Star Dust Canvas
          AnimatedBuilder(
            animation: _starController,
            builder: (context, child) {
              return CustomPaint(
                size: Size.infinite,
                painter: StarryDustPainter(animationValue: _starController.value),
              );
            },
          ),

          // 3. Main Scrollable Dashboard Content
          SafeArea(
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(parent: BouncingScrollPhysics()),
              padding: const EdgeInsets.fromLTRB(20, 16, 20, 96),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Top Header Bar
                  _buildHeader(),

                  if (_statusNotice != null) ...[
                    const SizedBox(height: 10),
                    _buildStatusNoticeBar(),
                  ],

                  const SizedBox(height: 20),

                  // Hero Circular Gauge
                  _buildHeroCircularGauge(),

                  // Dynamic Warning Capsule: Sleek muted dark card with soft warm accent
                  if (_insideHazardZone) ...[
                    const SizedBox(height: 16),
                    _buildHazardZoneGlowingAlert(),
                  ],

                  const SizedBox(height: 20),

                  // Weather Pill Row (3 micro-cards)
                  _buildWeatherPillRow(),

                  // Plume Warning Banner
                  if (!_insideHazardZone && _feedData.activeWarnings.isNotEmpty) ...[
                    const SizedBox(height: 18),
                    _buildPlumeWarningBanner(),
                  ],

                  const SizedBox(height: 22),

                  // Hyperlocal Sensor Mesh List
                  _buildSensorMeshSection(),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ==========================================================================
  // Header: "VaayuNetra Radar" • "Patna West Corridor" • "Live Telemetry"
  // ==========================================================================
  Widget _buildHeader() {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'VaayuNetra Radar',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 22,
                  fontWeight: FontWeight.w700,
                  letterSpacing: -0.3,
                ),
              ),
              const SizedBox(height: 4),
              _buildLocationSubtitle(),
            ],
          ),
        ),

        // Live Telemetry status pill + Action buttons
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
              decoration: BoxDecoration(
                color: const Color(0xFF133526),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFF22C55E).withValues(alpha: 0.35)),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 7,
                    height: 7,
                    decoration: const BoxDecoration(
                      color: Color(0xFF22C55E),
                      shape: BoxShape.circle,
                      boxShadow: [
                        BoxShadow(
                          color: Color(0xFF22C55E),
                          blurRadius: 6,
                          spreadRadius: 1,
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 6),
                  const Text(
                    'Live Telemetry',
                    style: TextStyle(
                      color: Color(0xFF86EFAC),
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                      letterSpacing: 0.2,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 8),

            // Gateway Settings
            IconButton(
              onPressed: _showGatewayDialog,
              icon: const Icon(Icons.tune_rounded, color: Color(0xFFAFA3CE), size: 19),
              tooltip: 'Gateway Settings',
              constraints: const BoxConstraints(minWidth: 32, minHeight: 32),
              padding: EdgeInsets.zero,
            ),

            // Refresh Button
            IconButton(
              onPressed: fetchHyperlocalData,
              icon: _isLoading
                  ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFFD3C1F5)),
                    )
                  : const Icon(Icons.refresh_rounded, color: Color(0xFFAFA3CE), size: 20),
              tooltip: 'Refresh Feed',
              constraints: const BoxConstraints(minWidth: 32, minHeight: 32),
              padding: EdgeInsets.zero,
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildLocationSubtitle() {
    if (isLocating) {
      return Row(
        mainAxisSize: MainAxisSize.min,
        children: const [
          Icon(Icons.location_on_rounded, color: Color(0xFFD3C1F5), size: 14),
          SizedBox(width: 5),
          CupertinoActivityIndicator(
            radius: 6,
            color: Color(0xFFD3C1F5),
          ),
          SizedBox(width: 6),
          Text(
            'Acquiring GPS fix...',
            style: TextStyle(
              color: Color(0xFFAFA3CE),
              fontSize: 13,
              fontWeight: FontWeight.w400,
            ),
          ),
        ],
      );
    }

    if (locationFailed) {
      return GestureDetector(
        onTap: fetchHyperlocalData,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
          decoration: BoxDecoration(
            color: const Color(0xFF38233C).withValues(alpha: 0.6),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: const Color(0xFFF87171).withValues(alpha: 0.35)),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: const [
              Icon(Icons.refresh_rounded, color: Color(0xFFFCA5A5), size: 13),
              SizedBox(width: 5),
              Text(
                "Couldn't locate • Tap to retry",
                style: TextStyle(
                  color: Color(0xFFFCA5A5),
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
      );
    }

    // Resolved state
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        const Icon(Icons.location_on_rounded, color: Color(0xFFD3C1F5), size: 14),
        const SizedBox(width: 4),
        Flexible(
          child: Text(
            locationName,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(
              color: Color(0xFFAFA3CE),
              fontSize: 13,
              fontWeight: FontWeight.w400,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildStatusNoticeBar() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: const Color(0xFF2E234A),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Text(
        _statusNotice!,
        style: const TextStyle(color: Color(0xFFD3C1F5), fontSize: 11.5),
      ),
    );
  }

  // ==========================================================================
  // Hero Circular Gauge: Large PM2.5 ("135.8") & "µg/m³ PM2.5 • Severe Hazard"
  // ==========================================================================
  Widget _buildHeroCircularGauge() {
    final pm25 = _feedData.streetPm25;
    final hazard = _feedData.hazardLevel;

    return Center(
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 16),
        decoration: BoxDecoration(
          color: const Color(0xFF201944).withValues(alpha: 0.65),
          borderRadius: BorderRadius.circular(28),
          border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.25),
              blurRadius: 20,
              offset: const Offset(0, 8),
            ),
          ],
        ),
        child: Column(
          children: [
            // Circular Radial Progress Gauge
            SizedBox(
              width: 190,
              height: 190,
              child: Stack(
                alignment: Alignment.center,
                children: [
                  CustomPaint(
                    size: const Size(190, 190),
                    painter: RadialGaugeRingPainter(
                      progress: (pm25 / 250.0).clamp(0.05, 1.0),
                    ),
                  ),
                  Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // Main value and unit subscript on the same horizontal line, baseline-aligned
                      FittedBox(
                        fit: BoxFit.scaleDown,
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          crossAxisAlignment: CrossAxisAlignment.baseline,
                          textBaseline: TextBaseline.alphabetic,
                          children: [
                            Text(
                              pm25.toStringAsFixed(1),
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 40,
                                fontWeight: FontWeight.w700,
                                letterSpacing: -1.0,
                              ),
                            ),
                            const SizedBox(width: 4),
                            const Text(
                              'µg/m³ PM₂.₅',
                              style: TextStyle(
                                color: Color(0xFFAFA3CE),
                                fontSize: 11.5,
                                fontWeight: FontWeight.w500,
                                letterSpacing: 0.1,
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 6),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 4),
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.08),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: Colors.white.withValues(alpha: 0.08),
                            width: 1,
                          ),
                        ),
                        child: Text(
                          'AQI ${_feedData.aqi}',
                          style: const TextStyle(
                            color: Color(0xFFFFB74D),
                            fontSize: 12,
                            fontWeight: FontWeight.w700,
                            letterSpacing: 0.3,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 14),

            // Hazard Status Pill Badge
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 5),
              decoration: BoxDecoration(
                color: _getGaugeColor(pm25).withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: _getGaugeColor(pm25).withValues(alpha: 0.3),
                  width: 1,
                ),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 6,
                    height: 6,
                    decoration: BoxDecoration(
                      color: _getGaugeColor(pm25),
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 7),
                  Text(
                    hazard,
                    style: TextStyle(
                      color: _getGaugeColor(pm25),
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      letterSpacing: 0.2,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Color _getGaugeColor(double pm25) {
    if (pm25 <= 35) return const Color(0xFF6ECBA8); // Sage Mint
    if (pm25 <= 75) return const Color(0xFFFBBF24); // Amber
    if (pm25 <= 120) return const Color(0xFFFFB74D); // Soft Amber
    return const Color(0xFFE57373); // Soft Warm Coral
  }

  // ==========================================================================
  // Dynamic Warning Capsule: Sleek muted dark card with soft warm accent
  // ==========================================================================
  Widget _buildHazardZoneGlowingAlert() {
    return _buildSleekAlertCard();
  }

  Widget _buildSleekAlertCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(
        color: const Color(0xFF1E1A29),
        borderRadius: BorderRadius.circular(14),
        border: const Border(
          left: BorderSide(color: Color(0xFFE57373), width: 4),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.25),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: const [
              Icon(
                Icons.warning_amber_rounded,
                color: Color(0xFFE57373),
                size: 18,
              ),
              SizedBox(width: 8),
              Text(
                'Active Smoke Plume Detected',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 0.1,
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            _getCleanAlertBody(),
            style: const TextStyle(
              color: Color(0xFFC7B8A8),
              fontSize: 12.5,
              fontWeight: FontWeight.w400,
              height: 1.4,
              letterSpacing: 0.1,
            ),
          ),
        ],
      ),
    );
  }

  String _getCleanAlertBody() {
    double? distKm;
    if (_feedData.activeWarnings.isNotEmpty) {
      distKm = _feedData.activeWarnings.first.distanceKm;
    }
    String distStr = "~10m";
    if (distKm != null && distKm > 0) {
      if (distKm < 0.05) {
        distStr = "~10m";
      } else if (distKm < 1.0) {
        distStr = "~${(distKm * 1000).toInt()}m";
      } else {
        distStr = "~${distKm.toStringAsFixed(1)} km";
      }
    } else if (_hazardMessage.isNotEmpty && _hazardMessage.contains('~')) {
      final match = RegExp(r'~[\d\.]+\s*(?:km|m)?').firstMatch(_hazardMessage);
      if (match != null) {
        distStr = match.group(0)!;
      }
    }
    return "A high-intensity biomass burning incident was reported $distStr from your area. Elevated PM2.5 detected in your dispersion corridor.";
  }

  // ==========================================================================
  // Weather Pill Row: 3 micro-cards (29°C Ambient, 68% Humidity, 11 km/h NE)
  // ==========================================================================
  Widget _buildWeatherPillRow() {
    return Row(
      children: [
        // 1. Ambient Temp
        Expanded(
          child: _buildWeatherMicroCard(
            icon: Icons.thermostat_rounded,
            iconColor: const Color(0xFFF6B26B),
            value: '${_feedData.tempC.toStringAsFixed(0)}°C',
            label: 'Ambient',
          ),
        ),
        const SizedBox(width: 10),

        // 2. Humidity
        Expanded(
          child: _buildWeatherMicroCard(
            icon: Icons.water_drop_rounded,
            iconColor: const Color(0xFF60A5FA),
            value: '${_feedData.humidity}%',
            label: 'Humidity',
          ),
        ),
        const SizedBox(width: 10),

        // 3. Dispersion Wind
        Expanded(
          child: _buildWeatherMicroCard(
            icon: Icons.air_rounded,
            iconColor: const Color(0xFFD3C1F5),
            value: '${_feedData.windSpeedKmh.toStringAsFixed(0)} km/h ${_feedData.windDirection}',
            label: 'Dispersion',
          ),
        ),
      ],
    );
  }

  Widget _buildWeatherMicroCard({
    required IconData icon,
    required Color iconColor,
    required String value,
    required String label,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 10),
      decoration: BoxDecoration(
        color: const Color(0xFF221A44).withValues(alpha: 0.65),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: Colors.white.withValues(alpha: 0.07)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.15),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          Icon(icon, color: iconColor, size: 20),
          const SizedBox(height: 6),
          FittedBox(
            fit: BoxFit.scaleDown,
            child: Text(
              value,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 14.5,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
          const SizedBox(height: 2),
          Text(
            label,
            style: const TextStyle(
              color: Color(0xFFAFA3CE),
              fontSize: 11,
              fontWeight: FontWeight.w400,
            ),
          ),
        ],
      ),
    );
  }

  // ==========================================================================
  // Plume Warning Banner: Sleek muted dark card with soft warm accent
  // ==========================================================================
  Widget _buildPlumeWarningBanner() {
    return _buildSleekAlertCard();
  }

  // ==========================================================================
  // Sensor Mesh List: 3 cards showing Node-VN-Alpha, Node-VN-Beta, Node-VN-Gamma
  // ==========================================================================
  Widget _buildSensorMeshSection() {
    final nodes = _feedData.groundSensors.isNotEmpty
        ? _feedData.groundSensors
        : FeedResponse.mockDefault().groundSensors;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Hyperlocal Sensor Mesh',
              style: TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.w600,
                letterSpacing: -0.2,
              ),
            ),
            Text(
              '3 Nodes Active',
              style: TextStyle(
                color: Color(0xFFAFA3CE),
                fontSize: 12,
                fontWeight: FontWeight.w400,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),

        // List of Sensor Mesh Nodes
        ...nodes.take(3).map((node) => _buildSensorMeshCard(node)),
      ],
    );
  }

  Widget _buildSensorMeshCard(SensorNode node) {
    final tagColor = _getStatusColor(node.aqiCategory);

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(
        color: const Color(0xFF1E173D).withValues(alpha: 0.72),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: Colors.white.withValues(alpha: 0.06)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.15),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          // Radio wave/sensor icon
          Container(
            padding: const EdgeInsets.all(9),
            decoration: BoxDecoration(
              color: const Color(0xFF292050),
              borderRadius: BorderRadius.circular(14),
            ),
            child: const Icon(Icons.sensors_rounded, color: Color(0xFFD3C1F5), size: 19),
          ),
          const SizedBox(width: 14),

          // Node ID & Distance
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  node.label.isNotEmpty ? node.label : node.sensorId,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 3),
                Text(
                  '${node.distanceKm.toStringAsFixed(1)} km away',
                  style: const TextStyle(
                    color: Color(0xFFAFA3CE),
                    fontSize: 11.5,
                    fontWeight: FontWeight.w400,
                  ),
                ),
              ],
            ),
          ),

          // PM2.5 Value & Status Tag
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '${node.pm25.toStringAsFixed(1)} µg/m³',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 14.5,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 3),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: tagColor.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: tagColor.withValues(alpha: 0.4), width: 0.8),
                ),
                child: Text(
                  node.aqiCategory,
                  style: TextStyle(
                    color: tagColor,
                    fontSize: 10.5,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Color _getStatusColor(String status) {
    final lower = status.toLowerCase();
    if (lower.contains('severe') || lower.contains('critical') || lower.contains('hazard')) {
      return const Color(0xFFF28D77); // Red/Coral
    }
    if (lower.contains('unhealthy') || lower.contains('poor')) {
      return const Color(0xFFF97316); // Orange
    }
    if (lower.contains('moderate')) {
      return const Color(0xFFFBBF24); // Amber
    }
    return const Color(0xFF6ECBA8); // Sage Mint
  }
}

// ============================================================================
// CustomPainter for Hero Circular Gauge Ring
// ============================================================================
class RadialGaugeRingPainter extends CustomPainter {
  final double progress; // 0.0 to 1.0
  final Color? strokeColor;

  RadialGaugeRingPainter({required this.progress, this.strokeColor});

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = (size.width / 2) - 12;
    final arcRect = Rect.fromCircle(center: center, radius: radius);

    // Background track ring (270 degrees arc)
    final trackPaint = Paint()
      ..color = Colors.white.withValues(alpha: 0.08)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 12
      ..strokeCap = StrokeCap.round;

    const startAngle = 0.75 * math.pi; // 135 deg
    const sweepAngle = 1.5 * math.pi; // 270 deg

    canvas.drawArc(
      arcRect,
      startAngle,
      sweepAngle,
      false,
      trackPaint,
    );

    // Soft smooth gradient (#E57373 to #FFB74D) with rounded stroke cap
    final gradientShader = const SweepGradient(
      startAngle: 0.75 * math.pi,
      endAngle: 2.25 * math.pi,
      colors: [
        Color(0xFFE57373), // Soft Warm Coral
        Color(0xFFFFB74D), // Soft Amber Gold
      ],
    ).createShader(arcRect);

    final progressPaint = Paint()
      ..shader = gradientShader
      ..style = PaintingStyle.stroke
      ..strokeWidth = 12
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      arcRect,
      startAngle,
      sweepAngle * progress,
      false,
      progressPaint,
    );
  }

  @override
  bool shouldRepaint(covariant RadialGaugeRingPainter oldDelegate) =>
      oldDelegate.progress != progress || oldDelegate.strokeColor != strokeColor;
}

// ============================================================================
// Background Cosmic Starry Dust Painter
// ============================================================================
class StarData {
  final double x;
  final double y;
  final double radius;
  final double opacity;
  const StarData(this.x, this.y, this.radius, this.opacity);
}

class StarryDustPainter extends CustomPainter {
  final double animationValue;

  StarryDustPainter({required this.animationValue});

  static const List<StarData> _stars = [
    StarData(0.12, 0.06, 1.2, 0.45),
    StarData(0.24, 0.12, 2.0, 0.65),
    StarData(0.85, 0.08, 1.4, 0.50),
    StarData(0.72, 0.18, 2.2, 0.70),
    StarData(0.08, 0.28, 1.0, 0.35),
    StarData(0.91, 0.32, 1.8, 0.60),
    StarData(0.55, 0.05, 1.1, 0.40),
    StarData(0.40, 0.16, 2.4, 0.75),
    StarData(0.62, 0.26, 1.3, 0.45),
    StarData(0.18, 0.45, 1.6, 0.55),
    StarData(0.82, 0.52, 1.2, 0.40),
    StarData(0.95, 0.68, 1.5, 0.50),
  ];

  @override
  void paint(Canvas canvas, Size size) {
    for (int i = 0; i < _stars.length; i++) {
      final s = _stars[i];
      final phase = (animationValue * 2 * math.pi) + (i * 0.5);
      final twinkle = 0.6 + 0.4 * math.sin(phase);
      final alpha = (s.opacity * twinkle).clamp(0.1, 0.95);

      final starPaint = Paint()
        ..color = (i % 3 == 0 ? const Color(0xFFD3C1F5) : Colors.white)
            .withValues(alpha: alpha);

      canvas.drawCircle(
        Offset(s.x * size.width, s.y * size.height),
        s.radius * (0.85 + 0.25 * twinkle),
        starPaint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant StarryDustPainter oldDelegate) =>
      oldDelegate.animationValue != animationValue;
}
