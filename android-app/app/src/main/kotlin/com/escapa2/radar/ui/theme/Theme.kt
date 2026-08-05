package com.escapa2.radar.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

private val LightColors = lightColorScheme(
    primary = Teal700,
    onPrimary = White,
    primaryContainer = Teal100,
    onPrimaryContainer = Teal900,
    secondary = Amber700,
    onSecondary = White,
    secondaryContainer = Amber100,
    onSecondaryContainer = Amber900,
    background = Grey50,
    surface = White,
)

private val DarkColors = darkColorScheme(
    primary = Teal300,
    onPrimary = Teal900,
    primaryContainer = Teal700,
    onPrimaryContainer = White,
    secondary = Amber300,
    onSecondary = Amber900,
    secondaryContainer = Amber700,
    onSecondaryContainer = White,
)

@Composable
fun Escapa2RadarTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit,
) {
    MaterialTheme(
        colorScheme = if (darkTheme) DarkColors else LightColors,
        typography = Typography,
        content = content,
    )
}
