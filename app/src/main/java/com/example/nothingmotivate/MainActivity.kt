package com.example.nothingmotivate

import android.content.Context
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Bolt
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.HourglassBottom
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.emptyPreferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.intPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.example.nothingmotivate.ui.theme.NothingMotivateTheme
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.launch

private val Context.dataStore by preferencesDataStore(name = "study_prefs")

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val dataStore = applicationContext.dataStore
        setContent {
            NothingMotivateTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    StudyDashboard(dataStore)
                }
            }
        }
    }
}

data class FocusStat(
    val title: String,
    val value: String,
    val accent: Color
)

data class SprintCue(
    val title: String,
    val subtitle: String,
    val iconTint: Color
)

@Composable
fun StudyDashboard(dataStore: DataStore<Preferences>) {
    val streakKey = remember { intPreferencesKey("streak") }
    val intentionKey = remember { stringPreferencesKey("intention") }
    val coroutineScope = rememberCoroutineScope()

    val defaultIntention = "Focus on understanding over speed."
    val streak by dataStore.data
        .collectAsState(initial = emptyPreferences())
        .let { it.value[streakKey] ?: 7 }

    val intention by dataStore.data
        .collectAsState(initial = emptyPreferences())
        .let { it.value[intentionKey] ?: defaultIntention }

    val tasks = remember {
        mutableStateListOf(
            "Review algorithms flashcards",
            "Summarize today's lecture",
            "30m problem set warmup"
        )
    }

    val stats = listOf(
        FocusStat("Streak", "${'$'}streak days", MaterialTheme.colorScheme.tertiary),
        FocusStat("Deep work", "2h 40m", MaterialTheme.colorScheme.primary),
        FocusStat("Energy", "82%", MaterialTheme.colorScheme.secondary),
        FocusStat("Completed", "12 tasks", MaterialTheme.colorScheme.inversePrimary)
    )

    val sprints = listOf(
        SprintCue("Start 25m focus", "Inspired by Nothing Essential", MaterialTheme.colorScheme.secondary),
        SprintCue("Reset posture", "Treat stillness as a feature", MaterialTheme.colorScheme.tertiary),
        SprintCue("Micro-journal", "Write one line intention", MaterialTheme.colorScheme.primary)
    )

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Text(
                text = "Nothing Study Companion",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.SemiBold
            )
            Text(
                text = "Built to be calm, minimal, and motivating.",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }

        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Default.Star,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.secondary
                        )
                        Text(
                            text = "${'$'}streak-day streak",
                            modifier = Modifier.padding(start = 8.dp),
                            style = MaterialTheme.typography.titleMedium
                        )
                    }
                    Spacer(modifier = Modifier.height(12.dp))
                    Text(
                        text = intention,
                        style = MaterialTheme.typography.bodyLarge,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    Spacer(modifier = Modifier.height(12.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        QuickAction(
                            label = "Re-center",
                            icon = Icons.Default.HourglassBottom,
                            onClick = {
                                coroutineScope.launch {
                                    dataStore.edit { prefs ->
                                        prefs[intentionKey] = "Breathe in, focus on the next block only."
                                    }
                                }
                            }
                        )
                        QuickAction(
                            label = "Small win",
                            icon = Icons.Default.CheckCircle,
                            onClick = {
                                coroutineScope.launch {
                                    dataStore.edit { prefs ->
                                        val current = prefs[streakKey] ?: 7
                                        prefs[streakKey] = current + 1
                                        prefs[intentionKey] = "Progress counts, momentum matters."
                                    }
                                }
                            }
                        )
                        QuickAction(
                            label = "Boost",
                            icon = Icons.Default.Bolt,
                            onClick = {
                                coroutineScope.launch {
                                    dataStore.edit { prefs ->
                                        prefs[intentionKey] = "Energy up: hydrate and stand for one minute."
                                    }
                                }
                            }
                        )
                    }
                }
            }
        }

        item {
            Text(
                text = "Today's Focus",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold
            )
            Spacer(modifier = Modifier.height(8.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                tasks.forEach { task ->
                    TaskPill(text = task)
                }
            }
        }

        item {
            Text(
                text = "Signals",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold
            )
            Spacer(modifier = Modifier.height(8.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                stats.chunked(2).firstOrNull()?.forEach { stat ->
                    StatCard(stat)
                }
            }
        }

        item {
            Text(
                text = "Study sprint cues",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold
            )
            Spacer(modifier = Modifier.height(8.dp))
        }

        items(sprints) { sprint ->
            SprintCard(sprint)
        }
    }
}

@Composable
fun QuickAction(label: String, icon: androidx.compose.ui.graphics.vector.ImageVector, onClick: () -> Unit) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier.clickable { onClick() }
    ) {
        Surface(
            modifier = Modifier.clip(MaterialTheme.shapes.small),
            color = MaterialTheme.colorScheme.primaryContainer
        ) {
            Icon(
                imageVector = icon,
                contentDescription = label,
                tint = MaterialTheme.colorScheme.onPrimaryContainer,
                modifier = Modifier.padding(10.dp)
            )
        }
        Text(
            text = label,
            style = MaterialTheme.typography.labelMedium,
            modifier = Modifier.padding(top = 6.dp)
        )
    }
}

@Composable
fun TaskPill(text: String) {
    Surface(
        color = MaterialTheme.colorScheme.primaryContainer,
        shape = MaterialTheme.shapes.small
    ) {
        Text(
            text = text,
            modifier = Modifier.padding(vertical = 8.dp, horizontal = 12.dp),
            style = MaterialTheme.typography.labelLarge
        )
    }
}

@Composable
fun StatCard(stat: FocusStat) {
    Card(
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
        modifier = Modifier.weight(1f)
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Text(text = stat.title, color = MaterialTheme.colorScheme.onSurfaceVariant)
            Text(
                text = stat.value,
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold,
                color = stat.accent
            )
        }
    }
}

@Composable
fun SprintCard(sprintCue: SprintCue) {
    Card(
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(text = sprintCue.title, style = MaterialTheme.typography.titleMedium)
                Text(
                    text = sprintCue.subtitle,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            Surface(
                color = sprintCue.iconTint.copy(alpha = 0.15f),
                shape = MaterialTheme.shapes.medium
            ) {
                Icon(
                    imageVector = Icons.Default.PlayArrow,
                    contentDescription = null,
                    tint = sprintCue.iconTint,
                    modifier = Modifier.padding(12.dp)
                )
            }
        }
    }
}

@Preview(showBackground = true)
@Composable
fun DashboardPreview() {
    NothingMotivateTheme {
        StudyDashboard(dataStore = FakeDataStore())
    }
}

// Preview-only DataStore stub
@Composable
private fun FakeDataStore(): DataStore<Preferences> = object : DataStore<Preferences> {
    override val data = flowOf(emptyPreferences())
    override suspend fun updateData(transform: suspend (t: Preferences) -> Preferences): Preferences = emptyPreferences()
}
