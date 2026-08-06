package com.escapa2.radar.ui.radar

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
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.escapa2.radar.R
import com.escapa2.radar.data.model.SearchWatch
import com.escapa2.radar.ui.components.UiState
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RadarScreen(viewModel: RadarViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val runningWatchId by viewModel.runningWatchId.collectAsStateWithLifecycle()
    val runMessage by viewModel.runMessage.collectAsStateWithLifecycle()
    val snackbarHostState = remember { SnackbarHostState() }

    val runErrorTemplate = stringResource(R.string.radar_run_error)
    val runNoAlerts = stringResource(R.string.radar_run_no_alerts)
    LaunchedEffect(runMessage) {
        when (val message = runMessage) {
            is RunMessage.Success -> {
                val text = if (message.result.alerts.isEmpty()) {
                    runNoAlerts
                } else {
                    message.result.alerts.joinToString("\n")
                }
                snackbarHostState.showSnackbar(text)
                viewModel.consumeRunMessage()
            }
            is RunMessage.Failure -> {
                snackbarHostState.showSnackbar(runErrorTemplate.format(message.message))
                viewModel.consumeRunMessage()
            }
            null -> Unit
        }
    }

    Scaffold(
        topBar = { TopAppBar(title = { Text(stringResource(R.string.radar_title)) }) },
        snackbarHost = { SnackbarHost(snackbarHostState) },
    ) { padding ->
        Column(modifier = Modifier.padding(padding)) {
            when (val state = uiState) {
                is UiState.Loading -> LoadingState(modifier = Modifier.weight(1f))
                is UiState.Empty -> EmptyState(modifier = Modifier.weight(1f))
                is UiState.Error -> ErrorState(
                    message = state.message,
                    onRetry = viewModel::load,
                    modifier = Modifier.weight(1f),
                )
                is UiState.Content -> ContentState(
                    watches = state.data,
                    runningWatchId = runningWatchId,
                    onRunWatch = viewModel::runWatch,
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
        modifier = modifier
            .fillMaxSize()
            .padding(24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(
            text = stringResource(R.string.radar_empty),
            style = MaterialTheme.typography.bodyLarge,
        )
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
    watches: List<SearchWatch>,
    runningWatchId: String?,
    onRunWatch: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    LazyColumn(
        modifier = modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item {
            Text(
                text = stringResource(R.string.radar_active_watches),
                style = MaterialTheme.typography.titleMedium,
            )
        }
        items(watches, key = { it.id }) { watch ->
            WatchCard(
                watch = watch,
                running = runningWatchId == watch.id,
                onRunWatch = { onRunWatch(watch.id) },
            )
        }
    }
}

@Composable
private fun WatchCard(
    watch: SearchWatch,
    running: Boolean,
    onRunWatch: () -> Unit,
) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = watch.name,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.weight(1f),
                )
                Text(
                    text = stringResource(R.string.radar_status_active),
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.primary,
                )
            }
            Text(
                text = "${stringResource(R.string.radar_last_run)} ${watch.lastRunAt}",
                style = MaterialTheme.typography.bodySmall,
            )
            Text(
                text = "${stringResource(R.string.radar_next_run)} ${watch.nextRunAt}",
                style = MaterialTheme.typography.bodySmall,
            )
            Column(modifier = Modifier.padding(top = 12.dp)) {
                val change = watch.changeSinceYesterdayEur
                Text(
                    text = "${stringResource(R.string.radar_change_since_yesterday)} " +
                        (change?.let { "${it.formatEur()} (${it.formatSigned()})" } ?: "—"),
                    style = MaterialTheme.typography.bodyMedium,
                    color = if (change != null && change < 0) {
                        MaterialTheme.colorScheme.primary
                    } else {
                        MaterialTheme.colorScheme.onSurface
                    },
                )
                Text(
                    text = "${stringResource(R.string.radar_min_recorded)} " +
                        (watch.minRecordedEur?.let { it.formatEur() } ?: "—"),
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
            Text(
                text = "${stringResource(R.string.radar_alert_rules)}: ${watch.alertRules.joinToString(", ")}",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.outline,
                modifier = Modifier.padding(top = 8.dp),
            )
            Text(
                text = "${stringResource(R.string.radar_price_history)}: " +
                    watch.priceHistory.joinToString { it.formatEur() },
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.outline,
            )
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 12.dp),
                horizontalArrangement = Arrangement.End,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                if (running) {
                    CircularProgressIndicator(modifier = Modifier.padding(end = 12.dp))
                    Text(
                        text = stringResource(R.string.radar_run_running),
                        style = MaterialTheme.typography.bodySmall,
                    )
                } else {
                    TextButton(onClick = onRunWatch) {
                        Text(stringResource(R.string.radar_run_now))
                    }
                }
            }
        }
    }
}

private fun Double.formatEur(): String =
    String.format(Locale("es", "ES"), "%.2f €", this)

private fun Double.formatSigned(): String =
    if (this < 0) {
        String.format(Locale("es", "ES"), "%.2f €", this)
    } else {
        String.format(Locale("es", "ES"), "+%.2f €", this)
    }
