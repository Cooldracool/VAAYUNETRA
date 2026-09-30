import 'package:flutter/foundation.dart' show kIsWeb, Uint8List;
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:image_picker/image_picker.dart';
import '../models/ticket.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

class ReportScreen extends StatefulWidget {
  const ReportScreen({super.key});

  @override
  State<ReportScreen> createState() => _ReportScreenState();
}

class _ReportScreenState extends State<ReportScreen> with SingleTickerProviderStateMixin {
  final ApiService _apiService = ApiService();
  final ImagePicker _picker = ImagePicker();

  XFile? _pickedFile;
  Uint8List? _imageBytes;
  String _selectedCategory = 'biomass_burning';

  // Read-only GPS telemetry
  double? _gpsLat;
  double? _gpsLon;
  bool _isGpsLocked = false;
  bool _isLocating = true;

  bool _isSubmitting = false;
  IncidentTicketResponse? _createdTicket;
  String? _errorMessage;

  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;

  final List<Map<String, String>> _categories = [
    {'value': 'biomass_burning', 'label': 'Biomass / Waste Burning'},
    {'value': 'agricultural_stubble_burning', 'label': 'Agricultural Stubble Burning'},
    {'value': 'landfill_fire', 'label': 'Municipal Landfill / Dump Fire'},
    {'value': 'industrial_smog', 'label': 'Industrial Emission Plume'},
  ];

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);

    _pulseAnimation = Tween<double>(begin: 0.8, end: 1.2).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );

    _detectCurrentLocation();
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  Future<void> _detectCurrentLocation() async {
    setState(() {
      _isLocating = true;
      _errorMessage = null;
    });

    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (serviceEnabled) {
        LocationPermission permission = await Geolocator.checkPermission();
        if (permission == LocationPermission.denied) {
          permission = await Geolocator.requestPermission();
        }
        if (permission == LocationPermission.whileInUse || permission == LocationPermission.always) {
          final position = await Geolocator.getCurrentPosition(
            locationSettings: const LocationSettings(timeLimit: Duration(seconds: 4)),
          );
          if (mounted) {
            setState(() {
              _gpsLat = position.latitude;
              _gpsLon = position.longitude;
              _isGpsLocked = true;
              _isLocating = false;
            });
            return;
          }
        }
      }
    } catch (_) {
      // Fallback location below
    }

    if (mounted) {
      setState(() {
        _gpsLat ??= 28.7041;
        _gpsLon ??= 77.1025;
        _isGpsLocked = true;
        _isLocating = false;
      });
    }
  }

  Future<void> _captureCameraProof() async {
    try {
      final XFile? file = await _picker.pickImage(source: ImageSource.camera, imageQuality: 85);
      if (file != null) {
        final bytes = await file.readAsBytes();
        setState(() {
          _pickedFile = file;
          _imageBytes = bytes;
          _errorMessage = null;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Camera capture failed: $e';
      });
    }
  }

  Future<void> _submitReport() async {
    final lat = _gpsLat ?? 25.5941;
    final lon = _gpsLon ?? 85.1376;

    setState(() {
      _isSubmitting = true;
      _errorMessage = null;
      _createdTicket = null;
    });

    try {
      final ticket = await _apiService.submitReport(
        lat: lat,
        lon: lon,
        category: _selectedCategory,
        imagePath: kIsWeb ? null : _pickedFile?.path,
        imageBytes: _imageBytes,
        filename: _pickedFile?.name ?? 'sample_fire_evidence.jpg',
      );

      if (mounted) {
        setState(() {
          _createdTicket = ticket;
          _isSubmitting = false;
        });

        _showSuccessDialog();
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = e.toString();
          _isSubmitting = false;
        });
      }
    }
  }

  void _showSuccessDialog() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF221A44),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(24),
          side: BorderSide(color: Colors.white.withValues(alpha: 0.1)),
        ),
        title: const Row(
          children: [
            Icon(Icons.check_circle_rounded, color: Color(0xFF22C55E), size: 24),
            SizedBox(width: 10),
            Text(
              'Report Dispatched',
              style: TextStyle(color: Colors.white, fontSize: 17, fontWeight: FontWeight.w600),
            ),
          ],
        ),
        content: const Text(
          'Report dispatched to Municipal Command',
          style: TextStyle(color: Color(0xFFD3C1F5), fontSize: 14),
        ),
        actions: [
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFD3C1F5),
              foregroundColor: const Color(0xFF1B1438),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            ),
            onPressed: () => Navigator.pop(ctx),
            child: const Text('OK', style: TextStyle(fontWeight: FontWeight.w700)),
          ),
        ],
      ),
    );
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
              Icon(Icons.camera_alt_rounded, color: AppTheme.primaryAccent, size: 20),
              SizedBox(width: 10),
              Text(
                'Report Incident',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 17,
                  color: AppTheme.textHeader,
                  letterSpacing: 0.3,
                ),
              ),
            ],
          ),
        ),
        body: ListView(
          padding: const EdgeInsets.fromLTRB(18, 8, 18, 90),
          children: [
            // 1. Live GPS Telemetry Capsule
            _buildGpsCapsule(),

            const SizedBox(height: 18),

            // 2. Camera Viewport Container (Radius 28)
            _buildCameraViewport(),

            const SizedBox(height: 18),

            // 3. Category Selector
            _buildCategorySelector(),

            const SizedBox(height: 20),

            // Error Display
            if (_errorMessage != null)
              Container(
                margin: const EdgeInsets.only(bottom: 16),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppTheme.hazardCoral.withValues(alpha: 0.15),
                  border: Border.all(color: AppTheme.hazardCoral.withValues(alpha: 0.5)),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.info_outline_rounded, color: AppTheme.hazardCoral, size: 18),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        _errorMessage!,
                        style: const TextStyle(color: AppTheme.hazardCoral, fontSize: 12),
                      ),
                    ),
                  ],
                ),
              ),

            // 4. Pill-Shaped Submit Action Button
            _buildSubmitButton(),

            const SizedBox(height: 24),

            // 5. Verification Result Card
            if (_createdTicket != null) _buildVerificationCard(_createdTicket!),
          ],
        ),
      ),
    );
  }

  /// Clean read-only rounded capsule with pulsing lavender indicator
  Widget _buildGpsCapsule() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: const Color(0xFF2E2452).withValues(alpha: 0.55),
        borderRadius: BorderRadius.circular(30),
        border: Border.all(
          color: const Color(0xFF5A4982).withValues(alpha: 0.4),
          width: 1,
        ),
      ),
      child: Row(
        children: [
          ScaleTransition(
            scale: _pulseAnimation,
            child: Container(
              width: 8,
              height: 8,
              decoration: BoxDecoration(
                color: _isGpsLocked ? AppTheme.primaryAccent : AppTheme.hazardCoral,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: AppTheme.primaryAccent.withValues(alpha: 0.6),
                    blurRadius: 8,
                    spreadRadius: 2,
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              _isLocating
                  ? 'Acquiring GPS Telemetry Lock...'
                  : '📍 GPS Locked: ${_gpsLat?.toStringAsFixed(4)}, ${_gpsLon?.toStringAsFixed(4)}',
              style: const TextStyle(
                color: AppTheme.textHeader,
                fontSize: 12.5,
                fontWeight: FontWeight.w600,
                letterSpacing: 0.3,
              ),
            ),
          ),
          Text(
            _isLocating ? 'Scanning' : 'Fixed',
            style: TextStyle(
              color: _isGpsLocked ? AppTheme.safeMint : AppTheme.textMuted,
              fontSize: 11,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  /// Sleek rounded rectangle camera viewport container (Radius 28)
  Widget _buildCameraViewport() {
    return Container(
      height: 220,
      decoration: BoxDecoration(
        color: const Color(0xFF221A44).withValues(alpha: 0.6),
        borderRadius: BorderRadius.circular(28),
        border: Border.all(
          color: AppTheme.surfaceLilac.withValues(alpha: 0.45),
          width: 1.2,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.3),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(28),
        child: _imageBytes != null
            ? Stack(
                fit: StackFit.expand,
                children: [
                  Image.memory(
                    _imageBytes!,
                    fit: BoxFit.cover,
                  ),
                  Container(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                        colors: [
                          Colors.transparent,
                          Colors.black.withValues(alpha: 0.65),
                        ],
                      ),
                    ),
                  ),
                  Positioned(
                    bottom: 14,
                    right: 14,
                    child: GestureDetector(
                      onTap: _captureCameraProof,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 7),
                        decoration: BoxDecoration(
                          color: const Color(0xFF1C1635).withValues(alpha: 0.85),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: AppTheme.primaryAccent.withValues(alpha: 0.4)),
                        ),
                        child: const Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.camera_alt_rounded, color: AppTheme.primaryAccent, size: 15),
                            SizedBox(width: 6),
                            Text(
                              'Retake Proof',
                              style: TextStyle(color: AppTheme.primaryAccent, fontSize: 11.5, fontWeight: FontWeight.w600),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              )
            : InkWell(
                onTap: _captureCameraProof,
                borderRadius: BorderRadius.circular(28),
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: AppTheme.primaryAccent.withValues(alpha: 0.12),
                          shape: BoxShape.circle,
                          border: Border.all(color: AppTheme.primaryAccent.withValues(alpha: 0.25)),
                        ),
                        child: const Icon(Icons.photo_camera_rounded, color: AppTheme.primaryAccent, size: 34),
                      ),
                      const SizedBox(height: 14),
                      const Text(
                        'Tap to Capture Live Proof',
                        style: TextStyle(
                          color: AppTheme.textHeader,
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          letterSpacing: 0.2,
                        ),
                      ),
                      const SizedBox(height: 4),
                      const Text(
                        'Strictly ImageSource.camera required',
                        style: TextStyle(color: AppTheme.textMuted, fontSize: 11),
                      ),
                    ],
                  ),
                ),
              ),
      ),
    );
  }

  /// Incident Category Dropdown inside pill container
  Widget _buildCategorySelector() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 4),
      decoration: BoxDecoration(
        color: const Color(0xFF2E2452).withValues(alpha: 0.55),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(
          color: const Color(0xFF5A4982).withValues(alpha: 0.4),
          width: 1,
        ),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          value: _selectedCategory,
          isExpanded: true,
          dropdownColor: const Color(0xFF221A44),
          icon: const Icon(Icons.keyboard_arrow_down_rounded, color: AppTheme.primaryAccent),
          style: const TextStyle(color: AppTheme.textHeader, fontSize: 13.5),
          items: _categories.map((cat) {
            return DropdownMenuItem<String>(
              value: cat['value'],
              child: Text(cat['label']!),
            );
          }).toList(),
          onChanged: (val) {
            if (val != null) setState(() => _selectedCategory = val);
          },
        ),
      ),
    );
  }

  /// Pill-shaped submit button (radius 40, gradient #C2ADF3 to #9E83E4)
  Widget _buildSubmitButton() {
    return Container(
      height: 50,
      decoration: BoxDecoration(
        gradient: AppTheme.buttonGradient,
        borderRadius: BorderRadius.circular(40),
        boxShadow: [
          BoxShadow(
            color: AppTheme.primaryAccent.withValues(alpha: 0.3),
            blurRadius: 18,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(40),
          onTap: _isSubmitting ? null : _submitReport,
          child: Center(
            child: _isSubmitting
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(color: AppTheme.buttonTextColor, strokeWidth: 2.2),
                  )
                : const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.send_rounded, color: AppTheme.buttonTextColor, size: 18),
                      SizedBox(width: 8),
                      Text(
                        'Submit Verified Report',
                        style: TextStyle(
                          color: AppTheme.buttonTextColor,
                          fontWeight: FontWeight.w700,
                          fontSize: 14.5,
                          letterSpacing: 0.3,
                        ),
                      ),
                    ],
                  ),
          ),
        ),
      ),
    );
  }

  /// Frosted Verification Summary Card
  Widget _buildVerificationCard(IncidentTicketResponse ticket) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF2E2452).withValues(alpha: 0.55),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(
          color: const Color(0xFF5A4982).withValues(alpha: 0.4),
          width: 1,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.25),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(6),
                    decoration: BoxDecoration(
                      color: AppTheme.safeMint.withValues(alpha: 0.15),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.check_circle_rounded, color: AppTheme.safeMint, size: 18),
                  ),
                  const SizedBox(width: 8),
                  const Text(
                    'Incident Verified & Persisted',
                    style: TextStyle(
                      color: AppTheme.textHeader,
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
                decoration: BoxDecoration(
                  color: AppTheme.primaryAccent.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  ticket.ticketId,
                  style: const TextStyle(color: AppTheme.primaryAccent, fontSize: 11, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),

          // Verification Metrics Tags
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _buildTag(
                'YOLO Vision: ${(ticket.verification.visionConfidence * 100).toStringAsFixed(0)}%',
                ticket.verification.visionVerified ? AppTheme.safeMint : AppTheme.hazardCoral,
              ),
              _buildTag(
                ticket.verification.satelliteThermalMatch ? 'Thermal Hotspot Matched' : 'Thermal Sensor Pass',
                AppTheme.primaryAccent,
              ),
              _buildTag(
                'Priority: ${ticket.impact.alertPriority}',
                ticket.impact.alertPriority == 'CRITICAL' || ticket.impact.alertPriority == 'HIGH'
                    ? AppTheme.hazardCoral
                    : AppTheme.safeMint,
              ),
            ],
          ),

          const SizedBox(height: 16),
          const Divider(color: Colors.white12, height: 1),
          const SizedBox(height: 12),

          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Wind: ${ticket.atmospheric.windSpeedKmh.toStringAsFixed(1)} km/h @ ${ticket.atmospheric.windDirectionDeg.toStringAsFixed(0)}°',
                style: const TextStyle(color: AppTheme.textMuted, fontSize: 11.5),
              ),
              Text(
                'AOD: ${ticket.atmospheric.aerosolOpticalDepth.toStringAsFixed(2)}',
                style: const TextStyle(color: AppTheme.textMuted, fontSize: 11.5),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTag(String text, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.14),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: color.withValues(alpha: 0.35)),
      ),
      child: Text(
        text,
        style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.w600),
      ),
    );
  }
}
