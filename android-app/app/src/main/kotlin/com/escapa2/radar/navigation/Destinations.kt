package com.escapa2.radar.navigation

import androidx.annotation.StringRes
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Explore
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Radar
import androidx.compose.ui.graphics.vector.ImageVector
import com.escapa2.radar.R

enum class Destination(
    val route: String,
    @StringRes val labelRes: Int,
    val icon: ImageVector,
) {
    HOME("home", R.string.nav_home, Icons.Filled.Home),
    EXPLORE("explore", R.string.nav_explore, Icons.Filled.Explore),
    RADAR("radar", R.string.nav_radar, Icons.Filled.Radar),
    PROFILE("profile", R.string.nav_profile, Icons.Filled.Person),
}

object OpportunityDetail {
    const val ARG_ID: String = "opportunityId"
    const val route: String = "opportunity/{$ARG_ID}"

    fun create(id: String): String = "opportunity/$id"
}
