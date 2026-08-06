package com.escapa2.radar

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.escapa2.radar.navigation.Escapa2NavHost
import com.escapa2.radar.ui.theme.Escapa2RadarTheme
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow

@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    private val _intents = MutableSharedFlow<Intent>(extraBufferCapacity = 1)

    /**
     * Incoming intents: the initial launch intent plus any delivered while the
     * activity is already running (singleTask), e.g. a push notification tap.
     */
    val intents: SharedFlow<Intent> = _intents

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        _intents.tryEmit(intent)
        enableEdgeToEdge()
        setContent {
            Escapa2RadarTheme {
                Escapa2NavHost(intentFlow = intents)
            }
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        _intents.tryEmit(intent)
    }
}
