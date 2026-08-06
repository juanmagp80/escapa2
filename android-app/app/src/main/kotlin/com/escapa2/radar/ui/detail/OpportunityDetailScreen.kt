package com.escapa2.radar.ui.detail

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Cancel
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalUriHandler
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.escapa2.radar.R
import com.escapa2.radar.data.model.AiSummary
import com.escapa2.radar.data.model.Opportunity
import com.escapa2.radar.data.model.PriceSnapshot
import com.escapa2.radar.ui.components.UiState
import java.util.Locale

@Composable
fun OpportunityDetailScreen(
    opportunityId: String,
    onBack: () -> Unit,
    viewModel: OpportunityDetailViewModel = hiltViewModel(),
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val summaryState by viewModel.summary.collectAsStateWithLifecycle()
    val priceHistory by viewModel.priceHistory.collectAsStateWithLifecycle()
    val followState by viewModel.followState.collectAsStateWithLifecycle()
    val snackbarHostState = remember { SnackbarHostState() }
    LaunchedEffect(opportunityId) { viewModel.load(opportunityId) }

    val followedMessage = stringResource(R.string.detail_follow_saved)
    val followErrorMessage = stringResource(R.string.detail_follow_error)
    LaunchedEffect(followState) {
        when (followState) {
            is UiState.Content -> snackbarHostState.showSnackbar(followedMessage)
            is UiState.Error -> snackbarHostState.showSnackbar(followErrorMessage)
            else -> Unit
        }
    }

    when (val state = uiState) {
        is UiState.Loading -> DetailScaffold(title = "", onBack = onBack, snackbarHostState = snackbarHostState) {
            Column(
                modifier = Modifier.fillMaxSize(),
                verticalArrangement = Arrangement.Center,
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                CircularProgressIndicator()
            }
        }
        is UiState.Empty -> DetailScaffold(title = "", onBack = onBack, snackbarHostState = snackbarHostState) {
            Text(
                text = stringResource(R.string.content_empty),
                style = MaterialTheme.typography.bodyLarge,
                modifier = Modifier.padding(24.dp),
            )
        }
        is UiState.Error -> DetailScaffold(title = "", onBack = onBack, snackbarHostState = snackbarHostState) {
            Column(modifier = Modifier.padding(24.dp)) {
                Text(
                    text = "${stringResource(R.string.content_error)} ${state.message}",
                    style = MaterialTheme.typography.bodyLarge,
                )
                Button(onClick = { viewModel.load(opportunityId) }, modifier = Modifier.padding(top = 12.dp)) {
                    Text(stringResource(R.string.content_retry))
                }
            }
        }
        is UiState.Content -> DetailContent(
            opportunity = state.data,
            summaryState = summaryState,
            priceHistoryState = priceHistory,
            followState = followState,
            onBack = onBack,
            onFollow = viewModel::follow,
            snackbarHostState = snackbarHostState,
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun DetailScaffold(
    title: String,
    onBack: () -> Unit,
    snackbarHostState: SnackbarHostState,
    content: @Composable () -> Unit,
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(title) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = stringResource(R.string.detail_back),
                        )
                    }
                },
            )
        },
        snackbarHost = { SnackbarHost(snackbarHostState) },
    ) { padding ->
        Column(modifier = Modifier.padding(padding)) { content() }
    }
}

@Composable
private fun DetailContent(
    opportunity: Opportunity,
    summaryState: UiState<AiSummary>?,
    priceHistoryState: UiState<List<PriceSnapshot>>?,
    followState: UiState<Unit>?,
    onBack: () -> Unit,
    onFollow: () -> Unit,
    snackbarHostState: SnackbarHostState,
) {
    DetailScaffold(
        title = opportunity.destinationName,
        onBack = onBack,
        snackbarHostState = snackbarHostState,
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Text(
                text = stringResource(transportLabel(opportunity.transportMode.name)),
                style = MaterialTheme.typography.labelLarge,
                color = MaterialTheme.colorScheme.primary,
            )
            Text(
                text = "${opportunity.startAt} → ${opportunity.endAt}",
                style = MaterialTheme.typography.bodyMedium,
            )
            HorizontalDivider()
            SectionCard(title = stringResource(R.string.detail_cost_summary)) {
                MetricRow(
                    label = stringResource(R.string.opportunity_total_for_two),
                    value = opportunity.totalCostEur.formatEur(),
                    emphasized = true,
                )
                MetricRow(
                    label = stringResource(R.string.detail_cost_per_person),
                    value = opportunity.costPerPersonEur.formatEur(),
                )
                MetricRow(
                    label = stringResource(R.string.detail_cost_per_night),
                    value = opportunity.costPerNightEur.formatEur(),
                )
            }
            SectionCard(title = stringResource(R.string.detail_useful_time)) {
                MetricRow(
                    label = stringResource(R.string.opportunity_useful_hours),
                    value = "${opportunity.usefulHours.toString().replace(".", ",")} h",
                )
                MetricRow(
                    label = stringResource(R.string.detail_cost_per_useful_hour),
                    value = "${opportunity.costPerUsefulHourEur.formatEur()}/h",
                )
            }
            CostBreakdownSection(opportunity = opportunity)
            BookingLinkSection(bookingUrl = opportunity.bookingUrl)
            PriceHistorySection(opportunity = opportunity, historyState = priceHistoryState)
            AiSummarySection(summaryState = summaryState)
            Button(
                onClick = onFollow,
                enabled = followState !is UiState.Loading,
                modifier = Modifier.fillMaxWidth(),
            ) {
                if (followState is UiState.Loading) {
                    CircularProgressIndicator(modifier = Modifier.size(20.dp))
                } else {
                    Text(stringResource(R.string.detail_follow_button))
                }
            }
            Text(
                text = "${stringResource(R.string.opportunity_verified)} ${opportunity.verifiedAt}",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.outline,
            )
            HorizontalDivider()
            Text(
                text = stringResource(R.string.detail_price_disclaimer),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.outline,
            )
            Spacer(modifier = Modifier.height(24.dp))
        }
    }
}

@Composable
private fun CostBreakdownSection(opportunity: Opportunity) {
    val items = buildList {
        opportunity.flightCostEur?.let { add(stringResource(R.string.detail_breakdown_flight) to it) }
        opportunity.hotelCostEur?.let { add(stringResource(R.string.detail_breakdown_hotel) to it) }
        opportunity.routeCostEur?.let { add(stringResource(R.string.detail_breakdown_route) to it) }
    }
    if (items.isEmpty()) return
    SectionCard(title = stringResource(R.string.detail_breakdown_title)) {
        items.forEach { (label, cost) ->
            MetricRow(label = label, value = cost.formatEur())
        }
    }
}

@Composable
private fun BookingLinkSection(bookingUrl: String?) {
    if (bookingUrl.isNullOrBlank()) return
    val uriHandler = LocalUriHandler.current
    SectionCard(title = stringResource(R.string.detail_booking_title)) {
        Text(
            text = stringResource(R.string.detail_booking_hint),
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.outline,
        )
        Button(
            onClick = { uriHandler.openUri(bookingUrl) },
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(stringResource(R.string.detail_booking_open))
        }
    }
}

@Composable
private fun PriceHistorySection(
    opportunity: Opportunity,
    historyState: UiState<List<PriceSnapshot>>?,
) {
    SectionCard(title = stringResource(R.string.detail_price_history)) {
        when (historyState) {
            null, is UiState.Loading -> CircularProgressIndicator(modifier = Modifier.padding(top = 8.dp))
            is UiState.Empty -> Unit
            is UiState.Error -> Unit
            is UiState.Content -> {
                historyState.data.forEachIndexed { index, snapshot ->
                    if (index > 0) {
                        Spacer(modifier = Modifier.height(4.dp))
                    }
                    MetricRow(
                        label = snapshot.capturedAt,
                        value = snapshot.totalCostEur?.formatEur() ?: "—",
                    )
                }
            }
        }
        val previous = opportunity.previousTotalCostEur
        if (previous != null && previous != opportunity.totalCostEur) {
            val change = previous - opportunity.totalCostEur
            HorizontalDivider(modifier = Modifier.padding(top = 8.dp, bottom = 8.dp))
            MetricRow(
                label = stringResource(R.string.detail_price_change),
                value = stringResource(
                    if (change < 0) {
                        R.string.home_biggest_drop_value
                    } else {
                        R.string.detail_price_rise
                    },
                    formatAmount(change),
                ),
            )
        }
        Text(
            text = stringResource(R.string.detail_price_history_note),
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.outline,
            modifier = Modifier.padding(top = 8.dp),
        )
    }
}

@Composable
private fun AiSummarySection(summaryState: UiState<AiSummary>?) {
    when (summaryState) {
        null, is UiState.Loading -> Unit
        is UiState.Empty -> Unit
        is UiState.Error -> Unit
        is UiState.Content -> {
            SectionCard(title = stringResource(R.string.detail_ai_summary)) {
                val summary = summaryState.data
                Text(
                    text = summary.headline,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary,
                )
                Text(
                    text = summary.summary,
                    style = MaterialTheme.typography.bodyMedium,
                )
                if (summary.pros.isNotEmpty()) {
                    summary.pros.forEach { pro ->
                        BulletRow(text = pro, positive = true)
                    }
                }
                if (summary.cons.isNotEmpty()) {
                    summary.cons.forEach { con ->
                        BulletRow(text = con, positive = false)
                    }
                }
                Text(
                    text = stringResource(
                        if (summary.generatedByAi) {
                            R.string.detail_ai_generated_by_ai
                        } else {
                            R.string.detail_ai_generated_by_rules
                        },
                    ),
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.outline,
                )
            }
        }
    }
}

@Composable
private fun BulletRow(text: String, positive: Boolean) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(
            imageVector = if (positive) {
                Icons.Filled.CheckCircle
            } else {
                Icons.Filled.Cancel
            },
            contentDescription = null,
            modifier = Modifier.size(12.dp),
            tint = if (positive) {
                MaterialTheme.colorScheme.primary
            } else {
                MaterialTheme.colorScheme.error
            },
        )
        Text(
            text = text,
            style = MaterialTheme.typography.bodyMedium,
            modifier = Modifier.padding(start = 8.dp),
        )
    }
}

@Composable
private fun SectionCard(
    title: String,
    content: @Composable () -> Unit,
) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
            )
            content()
        }
    }
}

@Composable
private fun MetricRow(
    label: String,
    value: String,
    emphasized: Boolean = false,
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            modifier = Modifier.weight(1f),
        )
        Text(
            text = value,
            style = if (emphasized) {
                MaterialTheme.typography.titleLarge
            } else {
                MaterialTheme.typography.titleMedium
            },
            fontWeight = FontWeight.Bold,
            color = if (emphasized) {
                MaterialTheme.colorScheme.primary
            } else {
                MaterialTheme.colorScheme.onSurface
            },
        )
    }
}

private fun transportLabel(value: String): Int = when (value) {
    "FLIGHT" -> R.string.transport_flight
    "CAR" -> R.string.transport_car
    else -> R.string.transport_either
}

private fun Double.formatEur(): String =
    String.format(Locale("es", "ES"), "%.2f €", this)

private fun formatAmount(value: Double): String =
    String.format(Locale("es", "ES"), "%.0f", value)
