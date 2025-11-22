package com.example.nothingmotivate.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.ColorScheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val DarkColorScheme: ColorScheme = darkColorScheme(
    primary = Mint,
    onPrimary = Color.Black,
    primaryContainer = GraphiteVariant,
    onPrimaryContainer = TextPrimary,
    secondary = AccentBlue,
    tertiary = AccentAmber,
    background = Graphite,
    surface = Graphite,
    surfaceVariant = GraphiteVariant,
    onSurface = TextPrimary,
    onSurfaceVariant = TextMuted,
    inversePrimary = AccentBlue
)

@Composable
fun NothingMotivateTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    MaterialTheme(
        colorScheme = DarkColorScheme,
        typography = Typography,
        content = content
    )
}
