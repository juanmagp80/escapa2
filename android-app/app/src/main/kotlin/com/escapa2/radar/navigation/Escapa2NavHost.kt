package com.escapa2.radar.navigation

import android.content.Intent
import androidx.compose.foundation.layout.padding
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import androidx.navigation.navDeepLink
import com.escapa2.radar.ui.components.ScaffoldWithBottomBar
import com.escapa2.radar.ui.detail.OpportunityDetailScreen
import com.escapa2.radar.ui.explore.ExploreScreen
import com.escapa2.radar.ui.home.HomeScreen
import com.escapa2.radar.ui.profile.ProfileScreen
import com.escapa2.radar.ui.radar.RadarScreen
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.collectLatest

@Composable
fun Escapa2NavHost(
    modifier: Modifier = Modifier,
    intentFlow: SharedFlow<Intent>? = null,
) {
    val navController = rememberNavController()
    val backStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = backStackEntry?.destination?.route

    LaunchedEffect(navController) {
        intentFlow?.collectLatest { intent ->
            if (intent.data?.scheme == DeepLinks.SCHEME) {
                navController.handleDeepLink(intent)
            }
        }
    }

    ScaffoldWithBottomBar(
        currentRoute = currentRoute,
        onNavigate = { destination ->
            navController.navigate(destination.route) {
                popUpTo(navController.graph.findStartDestination().id) {
                    saveState = true
                }
                launchSingleTop = true
                restoreState = true
            }
        },
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Destination.HOME.route,
            modifier = modifier.padding(innerPadding),
        ) {
            composable(Destination.HOME.route) {
                HomeScreen(
                    onSearchClick = {
                        navController.navigate(Destination.EXPLORE.route) {
                            launchSingleTop = true
                        }
                    },
                    onOpportunityClick = { opportunityId ->
                        navController.navigate(OpportunityDetail.create(opportunityId))
                    },
                )
            }
            composable(
                route = OpportunityDetail.route,
                arguments = listOf(
                    navArgument(OpportunityDetail.ARG_ID) { type = NavType.StringType },
                ),
            ) { backStackEntry ->
                val opportunityId = backStackEntry.arguments
                    ?.getString(OpportunityDetail.ARG_ID).orEmpty()
                OpportunityDetailScreen(
                    opportunityId = opportunityId,
                    onBack = { navController.popBackStack() },
                )
            }
            composable(Destination.EXPLORE.route) {
                ExploreScreen(
                    onOpportunityClick = { opportunityId ->
                        navController.navigate(OpportunityDetail.create(opportunityId))
                    },
                )
            }
            composable(
                route = Destination.RADAR.route,
                deepLinks = listOf(navDeepLink { uriPattern = DeepLinks.RADAR }),
            ) {
                RadarScreen()
            }
            composable(Destination.PROFILE.route) {
                ProfileScreen()
            }
        }
    }
}
