import 'package:flutter/material.dart';
import 'screens/municipal_map_screen.dart';
import 'screens/radar_screen.dart';
import 'screens/report_screen.dart';
import 'theme/app_theme.dart';

void main() {
  runApp(const VaayuNetraApp());
}

class VaayuNetraApp extends StatelessWidget {
  const VaayuNetraApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'VaayuNetra',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.themeData,
      home: const MainNavigationScreen(),
    );
  }
}

class MainNavigationScreen extends StatefulWidget {
  const MainNavigationScreen({super.key});

  @override
  State<MainNavigationScreen> createState() => _MainNavigationScreenState();
}

class _MainNavigationScreenState extends State<MainNavigationScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = const [
    RadarScreen(),
    ReportScreen(),
    MunicipalMapScreen(),
  ];

  Widget _buildNavItem(int index, IconData icon, String label) {
    final isSelected = _currentIndex == index;
    return GestureDetector(
      onTap: () => setState(() => _currentIndex = index),
      behavior: HitTestBehavior.opaque,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 4),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              size: 22,
              color: isSelected ? Colors.white : AppTheme.textSubtitles.withValues(alpha: 0.6),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                color: isSelected ? Colors.white : AppTheme.textSubtitles.withValues(alpha: 0.6),
                fontSize: 10.5,
                fontWeight: isSelected ? FontWeight.w500 : FontWeight.w300,
                letterSpacing: 0.1,
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBody: true,
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: SafeArea(
        child: Container(
          margin: const EdgeInsets.fromLTRB(28, 0, 28, 12),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          decoration: BoxDecoration(
            color: const Color(0xFF171530).withValues(alpha: 0.72),
            borderRadius: BorderRadius.circular(32),
            border: Border.all(
              color: Colors.white.withValues(alpha: 0.06),
              width: 1,
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.25),
                blurRadius: 20,
                offset: const Offset(0, 6),
              ),
            ],
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildNavItem(0, Icons.blur_on_rounded, 'Radar'),
              _buildNavItem(1, Icons.camera_alt_outlined, 'Report'),
              _buildNavItem(2, Icons.public_rounded, 'Map'),
            ],
          ),
        ),
      ),
    );
  }
}
