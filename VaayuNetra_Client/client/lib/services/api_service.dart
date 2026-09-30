import 'dart:convert';
import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb, Uint8List;
import 'package:http/http.dart' as http;
import '../models/ticket.dart';

class ApiService {
  static String? customBaseUrl;

  static String get baseUrl {
    if (customBaseUrl != null && customBaseUrl!.trim().isNotEmpty) {
      return customBaseUrl!.trim();
    }
    if (kIsWeb) {
      return 'http://127.0.0.1:8000';
    }
    try {
      if (Platform.isAndroid) {
        return 'http://10.0.2.2:8000';
      }
    } catch (_) {
      // Platform check may fail on some web runtimes
    }
    return 'http://127.0.0.1:8000';
  }

  /// Fetch localized citizen feed including ambient PM2.5, ground IoT sensors, and plume alerts.
  Future<FeedResponse> getFeed([double? lat, double? lon, String? fallbackLocation]) async {
    try {
      final url = (lat != null && lon != null)
          ? '$baseUrl/api/v1/feed?lat=$lat&lon=$lon'
          : '$baseUrl/api/v1/feed';
      final uri = Uri.parse(url);
      final response = await http.get(uri).timeout(const Duration(seconds: 4));

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
        return FeedResponse.fromJson(data);
      }
    } catch (_) {
      // Fall back safely to mock default
    }
    return FeedResponse.mockDefault(
      location: fallbackLocation ?? 'Pune Central Corridor',
      lat: lat ?? 18.5204,
      lon: lon ?? 73.8567,
    );
  }

  /// Reverse geocode coordinates to actual city/locality name using Nominatim OpenStreetMap API.
  Future<String?> reverseGeocode(double lat, double lon) async {
    try {
      final uri = Uri.parse('https://nominatim.openstreetmap.org/reverse?lat=$lat&lon=$lon&format=json');
      final response = await http.get(
        uri,
        headers: {'User-Agent': 'VaayuNetra-Municipal/1.0 (contact: support@vaayunetra.gov.in)'},
      ).timeout(const Duration(seconds: 4));

      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
        final address = data['address'] as Map<String, dynamic>? ?? {};

        final locality = address['suburb'] ??
            address['neighbourhood'] ??
            address['residential'] ??
            address['locality'] ??
            address['city_district'];

        final city = address['city'] ??
            address['town'] ??
            address['municipality'] ??
            address['county'] ??
            address['state_district'];

        if (locality != null && city != null) {
          return '$locality, $city';
        } else if (city != null) {
          return city as String;
        } else if (data['name'] != null && (data['name'] as String).isNotEmpty) {
          return data['name'] as String;
        } else if (data['display_name'] != null) {
          final parts = (data['display_name'] as String).split(',');
          if (parts.length >= 2) {
            return '${parts[0].trim()}, ${parts[1].trim()}';
          }
          return parts[0].trim();
        }
      }
    } catch (_) {}
    return null;
  }

  static final Uint8List defaultSampleFireImage = Uint8List.fromList([
    0xFF, 0xD8, 0xFF, 0xDB, 0x00, 0x43, 0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08, 0x07, 0x07,
    0x07, 0x09, 0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12, 0x13, 0x0F,
    0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20, 0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C,
    0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29, 0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D,
    0x38, 0x32, 0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01, 0x00, 0x01,
    0x01, 0x01, 0x11, 0x00, 0xFF, 0xC4, 0x00, 0x1F, 0x00, 0x00, 0x01, 0x05, 0x01, 0x01, 0x01, 0x01,
    0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06,
    0x07, 0x08, 0x09, 0x0A, 0x0B, 0xFF, 0xDA, 0x00, 0x08, 0x01, 0x01, 0x00, 0x00, 0x3F, 0x00, 0xBF,
    0x80, 0xFF, 0xD9
  ]);

  /// Submit an incident report with photographic evidence or sample fire image.
  Future<IncidentTicketResponse> submitReport({
    required double lat,
    required double lon,
    required String category,
    String? imagePath,
    Uint8List? imageBytes,
    String filename = 'sample_fire_evidence.jpg',
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/report');
    final request = http.MultipartRequest('POST', uri);

    request.fields['latitude'] = lat.toString();
    request.fields['longitude'] = lon.toString();
    request.fields['category'] = category;

    final bytesToSend = imageBytes ?? (imagePath == null ? defaultSampleFireImage : null);

    if (bytesToSend != null && bytesToSend.isNotEmpty) {
      request.files.add(
        http.MultipartFile.fromBytes(
          'file',
          bytesToSend,
          filename: filename,
        ),
      );
    } else if (imagePath != null && imagePath.isNotEmpty) {
      request.files.add(
        await http.MultipartFile.fromPath(
          'file',
          imagePath,
          filename: filename,
        ),
      );
    } else {
      request.files.add(
        http.MultipartFile.fromBytes(
          'file',
          defaultSampleFireImage,
          filename: filename,
        ),
      );
    }

    final streamedResponse = await request.send().timeout(const Duration(seconds: 15));
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200 || response.statusCode == 201) {
      final data = jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
      return IncidentTicketResponse.fromJson(data);
    } else {
      throw Exception('Failed to submit report (${response.statusCode}): ${response.body}');
    }
  }

  /// Spatial plume detection check returning hazard zone status for current coordinates.
  Future<Map<String, dynamic>> checkAlerts(double lat, double lon) async {
    try {
      final uri = Uri.parse('$baseUrl/api/v1/alerts/check?lat=$lat&lon=$lon');
      final response = await http.get(uri).timeout(const Duration(seconds: 4));

      if (response.statusCode == 200) {
        return jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
      }
    } catch (_) {
      // Fallback response if offline
    }
    return {
      'inside_hazard_zone': true,
      'hazard_type': 'smoke_plume_dispersion',
      'distance_km': 1.2,
      'severity': 'high',
      'message': 'Hazard Zone: You are inside the downwind smoke dispersion path (~1.2 km from reported fire).'
    };
  }

  /// Fetch GeoJSON FeatureCollection uniting all municipal incident origins and dispersion plumes.
  Future<Map<String, dynamic>> getMunicipalIncidents() async {
    final uri = Uri.parse('$baseUrl/api/v1/municipal/incidents');
    final response = await http.get(uri).timeout(const Duration(seconds: 10));

    if (response.statusCode == 200) {
      return jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
    } else {
      throw Exception('Failed to fetch municipal incidents (${response.statusCode}): ${response.body}');
    }
  }

  /// Trigger a live pitch demonstration spike.
  Future<IncidentTicketResponse> simulateSpike({
    required double lat,
    required double lon,
    String category = 'biomass_burning',
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/simulate/spike');
    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'latitude': lat,
        'longitude': lon,
        'category': category,
      }),
    ).timeout(const Duration(seconds: 10));

    if (response.statusCode == 201) {
      final data = jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
      return IncidentTicketResponse.fromJson(data);
    } else {
      throw Exception('Simulation failed (${response.statusCode}): ${response.body}');
    }
  }
}
