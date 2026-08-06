package com.escapa2.radar

import android.app.Application
import com.escapa2.radar.data.device.DeviceRegistrar
import dagger.hilt.android.HiltAndroidApp
import javax.inject.Inject

@HiltAndroidApp
class Escapa2Application : Application() {

    @Inject
    lateinit var deviceRegistrar: DeviceRegistrar

    override fun onCreate() {
        super.onCreate()
        deviceRegistrar.initialize()
    }
}
