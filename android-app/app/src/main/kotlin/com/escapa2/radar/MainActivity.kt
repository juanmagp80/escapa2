package com.escapa2.radar

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.escapa2.radar.navigation.Escapa2NavHost
import com.escapa2.radar.ui.theme.Escapa2RadarTheme
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            Escapa2RadarTheme {
                Escapa2NavHost()
            }
        }
    }
}
