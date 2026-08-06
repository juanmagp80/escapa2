package com.escapa2.radar.ui.home

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.escapa2.radar.R
import com.escapa2.radar.data.model.AvailabilityWindow
import com.escapa2.radar.data.model.Opportunity
import com.escapa2.radar.data.model.SearchWatch
import com.escapa2.radar.ui.components.OpportunityCard
import com.escapa2.radar.ui.components.UiState
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    onSearchClick: () -> Unit,
    onOpportunityClick: (String) -> Unit,
    viewModel: HomeViewModel = hiltViewModel(),
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    Scaffold(
        topBar = { TopAppBar(title = { Text(stringResource(R.string.home_title)) }) },
    ) { padding ->
        Column(modifier = Modifier.padding(padding)) {
            Button(
                onClick = onSearchClick,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
            ) {
                Text(stringResource(R.string.home_search_button))
            }
            when (val state = uiState) {
                is UiState.Loading -> LoadingState(modifier = Modifier.weight(1f))
                is UiState.Empty -> EmptyState(modifier = Modifier.weight(1f))
                is UiState.Error -> ErrorState(
                    message = state.message,
                    onRetry = viewModel::load,
                    modifier = Modifier.weight(1f),
                )
                is UiState.Content -> ContentState(
                    dashboard = state.data,
                    onOpportunityClick = onOpportunityClick,
                    modifier = Modifier.weight(1f),
                )
            }
        }
    }
}

@Composable
private fun LoadingState(modifier: Modifier = Modifier) {
    Column(
        modifier = modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        CircularProgressIndicator()
    }
}

@Composable
private fun EmptyState(modifier: Modifier = Modifier) {
    Column(
        modifier = modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(stringResource(R.string.content_empty), style = MaterialTheme.typography.bodyLarge)
    }
}

@Composable
private fun ErrorState(message: String, onRetry: () -> Unit, modifier: Modifier = Modifier) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(
            text = "${stringResource(R.string.content_error)} $message",
            style = MaterialTheme.typography.bodyLarge,
        )
        Button(onClick = onRetry, modifier = Modifier.padding(top = 12.dp)) {
            Text(stringResource(R.string.content_retry))
        }
    }
}

@Composable
private fun ContentState(
    dashboard: HomeDashboard,
    onOpportunityClick: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    LazyColumn(
        modifier = modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item {
            LastUpdateBanner(lastUpdateAt = dashboard.lastUpdateAt)
        }
        dashboard.bestOpportunity?.let { best ->
            item {
                SectionTitle(stringResource(R.string.home_best_opportunity))
            }
            item {
                OpportunityCard(
                    opportunity = best,
                    onClick = { onOpportunityClick(best.id) },
                )
            }
        }
        dashboard.biggestDrop?.let { drop ->
            item {
                SectionTitle(stringResource(R.string.home_biggest_drop))
            }
            item {
                PriceDropCard(
                    opportunity = drop,
                    onClick = { onOpportunityClick(drop.id) },
                )
            }
        }
        if (dashboard.availabilityWindows.isNotEmpty()) {
            item {
                SectionTitle(stringResource(R.string.home_next_free_dates))
            }
            dashboard.availabilityWindows.forEach { window ->
                item {
                    AvailabilityCard(window = window)
                }
            }
        }
        item {
            SectionTitle(stringResource(R.string.home_watches))
        }
        if (dashboard.watches.isEmpty()) {
            item {
                Text(
                    text = stringResource(R.string.home_watch_empty),
                    style = MaterialTheme.typography.bodyMedium,
                    modifier = Modifier.padding(vertical = 4.dp),
                )
            }
        } else {
            items(dashboard.watches, key = { "watch-${it.id}" }) { watch ->
                WatchCard(watch = watch)
            }
        }
        item {
            SectionTitle(stringResource(R.string.home_all_opportunities))
        }
        items(dashboard.opportunities, key = { "opp-${it.id}" }) { opportunity ->
            OpportunityCard(
                opportunity = opportunity,
                onClick = { onOpportunityClick(opportunity.id) },
            )
        }
    }
}

@Composable
private fun SectionTitle(text: String, modifier: Modifier = Modifier) {
    Text(
        text = text,
        style = MaterialTheme.typography.titleMedium,
        fontWeight = FontWeight.Bold,
        modifier = modifier.padding(top = 4.dp),
    )
}

@Composable
private fun AvailabilityCard(window: AvailabilityWindow, modifier: Modifier = Modifier) {
    Card(modifier = modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = windowKindLabel(window.kind),
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.primary,
            )
            Text(
                text = "${window.startAt} → ${window.endAt}",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
            )
            Text(
                text = if (window.isFlexible) {
                    stringResource(R.string.home_availability_flexible)
                } else {
                    stringResource(R.string.home_availability_fixed)
                },
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.outline,
            )
        }
    }
}

private fun windowKindLabel(kind: String): String = when (kind) {
    "WEEKEND" -> "Fin de semana"
    "VACATION" -> "Vacaciones"
    else -> kind
}

@Composable
private fun LastUpdateBanner(lastUpdateAt: String?, modifier: Modifier = Modifier) {
    Card(modifier = modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = stringResource(R.string.home_last_update),
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.outline,
            )
            Text(
                text = lastUpdateAt ?: stringResource(R.string.home_last_update_never),
                style = MaterialTheme.typography.bodyMedium,
            )
        }
    }
}

@Composable
private fun PriceDropCard(
    opportunity: Opportunity,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val dropAmount = opportunity.previousTotalCostEur?.minus(opportunity.totalCostEur) ?: 0.0
    Card(modifier = modifier.fillMaxWidth(), onClick = onClick) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = opportunity.destinationName,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
            )
            Text(
                text = stringResource(R.string.home_biggest_drop_value, formatAmount(dropAmount)),
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary,
            )
            Text(
                text = "${opportunity.totalCostEur.formatEur()} ${stringResource(R.string.home_verified)} " +
                    opportunity.verifiedAt,
                style = MaterialTheme.typography.bodyMedium,
            )
        }
    }
}

@Composable
private fun WatchCard(watch: SearchWatch, modifier: Modifier = Modifier) {
    Card(modifier = modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = watch.name,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                )
                Text(
                    text = watchChangeText(watch),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.outline,
                )
            }
            Text(
                text = watch.minRecordedEur?.formatEur().orEmpty(),
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
            )
        }
    }
}

@Composable
private fun watchChangeText(watch: SearchWatch): String {
    val change = watch.changeSinceYesterdayEur ?: 0.0
    return if (change < 0) {
        stringResource(R.string.home_watch_change_down, formatAmount(-change))
    } else {
        stringResource(R.string.home_watch_change_flat)
    }
}

private fun formatAmount(value: Double): String =
    String.format(Locale("es", "ES"), "%.0f", value)

private fun Double.formatEur(): String =
    String.format(Locale("es", "ES"), "%.2f €", this)
