import 'package:flutter/material.dart';

/// Design tokens and styles for VaayuNetra's dreamy, celestial midnight-lavender aesthetic.
/// Inspired by starry nights, soft planetary curved layouts, and storybook minimalism.
class AppTheme {
  // Background Canvas: Solid deep matte midnight #171530 to #231E44
  static const LinearGradient backgroundGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [
      Color(0xFF171530),
      Color(0xFF231E44),
      Color(0xFF171530),
    ],
  );

  static const Color backgroundCanvas = Color(0xFF171530);
  static const Color backgroundMid = Color(0xFF231E44);

  // Planet Horizon Gradient (#B8A9D9 light crest highlight to #4E4374 and deep shadow)
  static const Color planetCrestHighlight = Color(0xFFB8A9D9);
  static const Color planetSurfaceMid = Color(0xFF7868A3);
  static const Color planetShadowDeep = Color(0xFF4E4374);

  // Text Palette
  static const Color textPrimary = Color(0xFFFFFFFF);
  static const Color textSubtitles = Color(0xFF9B94B8);
  static const Color textHeader = Color(0xFFFFFFFF);
  static const Color textMuted = Color(0xFF9B94B8);

  // Action Pill (Smooth porcelain/cream pill with diffused lavender shadow)
  static const Color porcelainPillBg = Color(0xFFF4EFFF);
  static const Color porcelainPillText = Color(0xFF241C42);
  static const BoxShadow porcelainPillShadow = BoxShadow(
    color: Color(0x33A694D1),
    blurRadius: 24,
    offset: Offset(0, 10),
  );

  // Subtle Alert Pill
  static const Color alertPillBg = Color(0xFF2A234A);
  static const Color alertPillText = Color(0xFFF2B89D);
  static const Color hazardCoral = Color(0xFFF2B89D);
  static const Color safeMint = Color(0xFF9DE0C0);

  // Accents & Nav
  static const Color primaryAccent = Color(0xFFD3C1F5);
  static const Color surfaceLilac = Color(0xFF9B94B8);
  static const Color navBackground = Color(0xFF1B1736);

  // Button Gradient for auxiliary actions
  static const LinearGradient buttonGradient = LinearGradient(
    colors: [Color(0xFFD3C1F5), Color(0xFFA694D1)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  static const Color buttonTextColor = Color(0xFF241C42);

  static ThemeData get themeData {
    return ThemeData(
      brightness: Brightness.dark,
      scaffoldBackgroundColor: backgroundCanvas,
      primaryColor: primaryAccent,
      colorScheme: const ColorScheme.dark(
        primary: primaryAccent,
        secondary: surfaceLilac,
        surface: backgroundMid,
        error: hazardCoral,
      ),
      fontFamily: 'Roboto',
      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: false,
        iconTheme: IconThemeData(color: primaryAccent),
        titleTextStyle: TextStyle(
          color: textPrimary,
          fontSize: 16,
          fontWeight: FontWeight.w400,
          letterSpacing: -0.2,
        ),
      ),
      useMaterial3: true,
    );
  }
}
