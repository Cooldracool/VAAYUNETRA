class AtmosphericSummary {
  final double windSpeedKmh;
  final double windDirectionDeg;
  final double temperatureC;
  final double regionalNo2Ugm3;
  final double aerosolOpticalDepth;

  AtmosphericSummary({
    required this.windSpeedKmh,
    required this.windDirectionDeg,
    required this.temperatureC,
    required this.regionalNo2Ugm3,
    required this.aerosolOpticalDepth,
  });

  factory AtmosphericSummary.fromJson(Map<String, dynamic> json) {
    return AtmosphericSummary(
      windSpeedKmh: (json['wind_speed_kmh'] as num?)?.toDouble() ?? 0.0,
      windDirectionDeg: (json['wind_direction_deg'] as num?)?.toDouble() ?? 0.0,
      temperatureC: (json['temperature_c'] as num?)?.toDouble() ?? 0.0,
      regionalNo2Ugm3: (json['regional_no2_ugm3'] as num?)?.toDouble() ?? 0.0,
      aerosolOpticalDepth: (json['aerosol_optical_depth'] as num?)?.toDouble() ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() => {
    'wind_speed_kmh': windSpeedKmh,
    'wind_direction_deg': windDirectionDeg,
    'temperature_c': temperatureC,
    'regional_no2_ugm3': regionalNo2Ugm3,
    'aerosol_optical_depth': aerosolOpticalDepth,
  };
}

class VerificationSummary {
  final bool visionVerified;
  final double visionConfidence;
  final bool satelliteThermalMatch;
  final double thermalDistanceM;

  VerificationSummary({
    required this.visionVerified,
    required this.visionConfidence,
    required this.satelliteThermalMatch,
    required this.thermalDistanceM,
  });

  factory VerificationSummary.fromJson(Map<String, dynamic> json) {
    return VerificationSummary(
      visionVerified: json['vision_verified'] as bool? ?? false,
      visionConfidence: (json['vision_confidence'] as num?)?.toDouble() ?? 0.0,
      satelliteThermalMatch: json['satellite_thermal_match'] as bool? ?? false,
      thermalDistanceM: (json['thermal_distance_m'] as num?)?.toDouble() ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() => {
    'vision_verified': visionVerified,
    'vision_confidence': visionConfidence,
    'satellite_thermal_match': satelliteThermalMatch,
    'thermal_distance_m': thermalDistanceM,
  };
}

class ImpactedReceptor {
  final String name;
  final String amenityType;
  final double distanceM;

  ImpactedReceptor({
    required this.name,
    required this.amenityType,
    required this.distanceM,
  });

  factory ImpactedReceptor.fromJson(Map<String, dynamic> json) {
    return ImpactedReceptor(
      name: json['name'] as String? ?? 'Community Facility',
      amenityType: json['amenity_type'] as String? ?? 'facility',
      distanceM: (json['distance_m'] as num?)?.toDouble() ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() => {
    'name': name,
    'amenity_type': amenityType,
    'distance_m': distanceM,
  };
}

class ImpactAssessment {
  final int vulnerabilityScore;
  final String alertPriority;
  final List<ImpactedReceptor> impactedReceptors;

  ImpactAssessment({
    required this.vulnerabilityScore,
    required this.alertPriority,
    required this.impactedReceptors,
  });

  factory ImpactAssessment.fromJson(Map<String, dynamic> json) {
    final receptorsList = json['impacted_receptors'] as List<dynamic>? ?? [];
    return ImpactAssessment(
      vulnerabilityScore: (json['vulnerability_score'] as num?)?.toInt() ?? 0,
      alertPriority: json['alert_priority'] as String? ?? 'MODERATE',
      impactedReceptors: receptorsList
          .map((item) => ImpactedReceptor.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }

  Map<String, dynamic> toJson() => {
    'vulnerability_score': vulnerabilityScore,
    'alert_priority': alertPriority,
    'impacted_receptors': impactedReceptors.map((r) => r.toJson()).toList(),
  };
}

class IncidentTicketResponse {
  final String ticketId;
  final String timestamp;
  final String category;
  final double latitude;
  final double longitude;
  final VerificationSummary verification;
  final AtmosphericSummary atmospheric;
  final ImpactAssessment impact;
  final Map<String, dynamic> plumeGeojson;

  IncidentTicketResponse({
    required this.ticketId,
    required this.timestamp,
    required this.category,
    required this.latitude,
    required this.longitude,
    required this.verification,
    required this.atmospheric,
    required this.impact,
    required this.plumeGeojson,
  });

  factory IncidentTicketResponse.fromJson(Map<String, dynamic> json) {
    return IncidentTicketResponse(
      ticketId: json['ticket_id'] as String? ?? 'VN-UNKNOWN',
      timestamp: json['timestamp'] as String? ?? '',
      category: json['category'] as String? ?? 'general',
      latitude: (json['latitude'] as num?)?.toDouble() ?? 0.0,
      longitude: (json['longitude'] as num?)?.toDouble() ?? 0.0,
      verification: VerificationSummary.fromJson(json['verification'] as Map<String, dynamic>? ?? {}),
      atmospheric: AtmosphericSummary.fromJson(json['atmospheric'] as Map<String, dynamic>? ?? {}),
      impact: ImpactAssessment.fromJson(json['impact'] as Map<String, dynamic>? ?? {}),
      plumeGeojson: json['plume_geojson'] as Map<String, dynamic>? ?? {},
    );
  }

  Map<String, dynamic> toJson() => {
    'ticket_id': ticketId,
    'timestamp': timestamp,
    'category': category,
    'latitude': latitude,
    'longitude': longitude,
    'verification': verification.toJson(),
    'atmospheric': atmospheric.toJson(),
    'impact': impact.toJson(),
    'plume_geojson': plumeGeojson,
  };
}

class SensorNode {
  final String sensorId;
  final String label;
  final double latitude;
  final double longitude;
  final double distanceKm;
  final double pm25;
  final double pm10;
  final String aqiCategory;
  final String timestamp;
  final String source;

  SensorNode({
    required this.sensorId,
    required this.label,
    required this.latitude,
    required this.longitude,
    required this.distanceKm,
    required this.pm25,
    required this.pm10,
    required this.aqiCategory,
    required this.timestamp,
    required this.source,
  });

  factory SensorNode.fromJson(Map<String, dynamic> json) {
    final idStr = json['id'] as String? ?? json['sensor_id'] as String? ?? 'VN-NODE';
    final labelStr = json['name'] as String? ?? json['label'] as String? ?? idStr;
    final pm25Val = (json['pm25'] as num?)?.toDouble() ??
        (json['pm2_5'] as num?)?.toDouble() ??
        0.0;
    final pm10Val = (json['pm10'] as num?)?.toDouble() ?? 0.0;
    final statusStr = json['status'] as String? ??
        json['aqi_category'] as String? ??
        'Moderate';

    return SensorNode(
      sensorId: idStr,
      label: labelStr,
      latitude: (json['latitude'] as num?)?.toDouble() ?? 0.0,
      longitude: (json['longitude'] as num?)?.toDouble() ?? 0.0,
      distanceKm: (json['distance_km'] as num?)?.toDouble() ?? 0.0,
      pm25: pm25Val,
      pm10: pm10Val,
      aqiCategory: statusStr,
      timestamp: json['timestamp'] as String? ?? '',
      source: json['source'] as String? ?? 'mesh',
    );
  }
}

class PlumeWarning {
  final String incidentId;
  final String category;
  final double originLat;
  final double originLon;
  final double distanceKm;
  final double windSpeedKmh;
  final double headingDeg;
  final int vulnerabilityScore;
  final String advisory;

  PlumeWarning({
    required this.incidentId,
    required this.category,
    required this.originLat,
    required this.originLon,
    this.distanceKm = 0.0,
    required this.windSpeedKmh,
    required this.headingDeg,
    required this.vulnerabilityScore,
    required this.advisory,
  });

  factory PlumeWarning.fromJson(Map<String, dynamic> json) {
    final msg = json['message'] as String? ?? json['advisory'] as String? ?? 'Downwind plume detected.';
    return PlumeWarning(
      incidentId: json['id'] as String? ?? json['incident_id'] as String? ?? 'VN-ALERT',
      category: json['severity'] as String? ?? json['category'] as String? ?? 'biomass_burning',
      originLat: (json['origin_lat'] as num?)?.toDouble() ?? 0.0,
      originLon: (json['origin_lon'] as num?)?.toDouble() ?? 0.0,
      distanceKm: (json['distance_km'] as num?)?.toDouble() ?? 0.0,
      windSpeedKmh: (json['wind_speed_kmh'] as num?)?.toDouble() ?? 0.0,
      headingDeg: (json['heading_deg'] as num?)?.toDouble() ?? 0.0,
      vulnerabilityScore: (json['vulnerability_score'] as num?)?.toInt() ?? 0,
      advisory: msg,
    );
  }
}

class FeedResponse {
  final String location;
  final String status;
  final int aqi;
  final String hazardLevel;
  final double tempC;
  final int humidity;
  final double windSpeedKmh;
  final String windDirection;
  final double streetPm25;
  final double pm10;
  final double latitude;
  final double longitude;
  final bool insideActivePlume;
  final List<PlumeWarning> activeWarnings;
  final List<SensorNode> groundSensors;
  final List<IncidentTicketResponse> activeIncidents;

  FeedResponse({
    this.location = 'Pune Central Corridor',
    this.status = 'online',
    this.aqi = 142,
    this.hazardLevel = 'Severe Hazard',
    this.tempC = 29.0,
    this.humidity = 68,
    this.windSpeedKmh = 11.0,
    this.windDirection = 'NE',
    required this.streetPm25,
    this.pm10 = 182.4,
    this.latitude = 18.5204,
    this.longitude = 73.8567,
    this.insideActivePlume = true,
    required this.activeWarnings,
    required this.groundSensors,
    this.activeIncidents = const [],
  });

  factory FeedResponse.fromJson(Map<String, dynamic> json) {
    final warningsList = (json['active_warnings'] as List<dynamic>?) ?? [];
    final sensorsList = (json['nearby_nodes'] as List<dynamic>?) ??
        (json['nearby_sensors'] as List<dynamic>?) ??
        (json['ground_sensors'] as List<dynamic>?) ??
        [];
    final incidentsList = (json['active_incidents'] as List<dynamic>?) ?? [];

    final weather = json['weather'] as Map<String, dynamic>? ?? {};

    final pm25Val = (json['pm25'] as num?)?.toDouble() ??
        (json['current_pm25'] as num?)?.toDouble() ??
        (json['street_pm2_5'] as num?)?.toDouble() ??
        135.8;

    final tempVal = (weather['temperature_c'] as num?)?.toDouble() ??
        (weather['temp_c'] as num?)?.toDouble() ??
        29.0;

    final humidVal = (weather['relative_humidity'] as num?)?.toInt() ??
        (weather['humidity'] as num?)?.toInt() ??
        68;

    final windSpd = (weather['wind_speed_kmh'] as num?)?.toDouble() ??
        ((weather['wind_speed_mps'] as num?) != null
            ? (weather['wind_speed_mps'] as num).toDouble() * 3.6
            : 11.0);

    final windDir = (weather['wind_cardinal'] as String?) ??
        (weather['wind_direction'] as String?) ??
        'NE';

    return FeedResponse(
      location: json['location'] as String? ?? 'Pune Central Corridor',
      status: json['status'] as String? ?? 'online',
      aqi: (json['aqi'] as num?)?.toInt() ?? 142,
      hazardLevel: json['hazard_level'] as String? ??
          json['aqi_category'] as String? ??
          'Severe Hazard',
      tempC: tempVal,
      humidity: humidVal,
      windSpeedKmh: windSpd,
      windDirection: windDir,
      streetPm25: pm25Val,
      pm10: (json['pm10'] as num?)?.toDouble() ?? 182.4,
      latitude: (json['latitude'] as num?)?.toDouble() ?? 18.5204,
      longitude: (json['longitude'] as num?)?.toDouble() ?? 73.8567,
      insideActivePlume: json['inside_active_plume'] as bool? ?? (warningsList.isNotEmpty),
      activeWarnings: warningsList
          .map((item) => PlumeWarning.fromJson(item as Map<String, dynamic>))
          .toList(),
      groundSensors: sensorsList
          .map((item) => SensorNode.fromJson(item as Map<String, dynamic>))
          .toList(),
      activeIncidents: incidentsList
          .map((item) => IncidentTicketResponse.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }

  static FeedResponse mockDefault({String location = 'Pune Central Corridor', double lat = 18.5204, double lon = 73.8567}) {
    return FeedResponse(
      location: location,
      status: 'online',
      aqi: 142,
      hazardLevel: 'Severe Hazard',
      tempC: 29.0,
      humidity: 68,
      windSpeedKmh: 11.0,
      windDirection: 'NE',
      streetPm25: 135.8,
      pm10: 182.4,
      latitude: lat,
      longitude: lon,
      insideActivePlume: true,
      activeWarnings: [
        PlumeWarning(
          incidentId: 'warn-101',
          category: 'biomass_burning',
          originLat: 25.5941,
          originLon: 85.1376,
          windSpeedKmh: 11.0,
          headingDeg: 45.0,
          vulnerabilityScore: 85,
          advisory: 'Unusual biomass smoke plume detected ~1.2 km upwind',
        ),
      ],
      groundSensors: [
        SensorNode(
          sensorId: 'Node-VN-Alpha',
          label: 'Node-VN-Alpha',
          latitude: 25.596,
          longitude: 85.139,
          distanceKm: 0.4,
          pm25: 138.4,
          pm10: 184.2,
          aqiCategory: 'Severe',
          timestamp: '',
          source: 'mesh',
        ),
        SensorNode(
          sensorId: 'Node-VN-Beta',
          label: 'Node-VN-Beta',
          latitude: 25.589,
          longitude: 85.128,
          distanceKm: 1.1,
          pm25: 112.0,
          pm10: 154.0,
          aqiCategory: 'Unhealthy',
          timestamp: '',
          source: 'mesh',
        ),
        SensorNode(
          sensorId: 'Node-VN-Gamma',
          label: 'Node-VN-Gamma',
          latitude: 25.578,
          longitude: 85.115,
          distanceKm: 1.8,
          pm25: 84.5,
          pm10: 118.0,
          aqiCategory: 'Moderate',
          timestamp: '',
          source: 'mesh',
        ),
      ],
      activeIncidents: [],
    );
  }
}
