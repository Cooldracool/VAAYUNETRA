import 'package:flutter_test/flutter_test.dart';
import 'package:client/main.dart';

void main() {
  testWidgets('VaayuNetra basic render smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const VaayuNetraApp());
    expect(find.text('Radar'), findsOneWidget);
    expect(find.text('VaayuNetra Radar'), findsOneWidget);
    expect(find.text('Live Telemetry'), findsOneWidget);
    expect(find.text('Acquiring GPS fix...'), findsOneWidget);
    expect(find.text('Active Smoke Plume Detected'), findsOneWidget);
    expect(find.text('µg/m³ PM₂.₅'), findsOneWidget);
  });
}
