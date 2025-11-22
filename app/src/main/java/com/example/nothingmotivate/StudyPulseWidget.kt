package com.example.nothingmotivate

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.Context
import android.content.Intent
import android.widget.RemoteViews

class StudyPulseWidget : AppWidgetProvider() {
    override fun onUpdate(context: Context, appWidgetManager: AppWidgetManager, appWidgetIds: IntArray) {
        appWidgetIds.forEach { appWidgetId ->
            updateAppWidget(context, appWidgetManager, appWidgetId)
        }
    }

    companion object {
        private val prompts = listOf(
            "Tap in. One mindful breath, then start.",
            "Noise-free zone: pick one task only.",
            "Monotask for 25 minutes, then reset.",
            "Motion unlocks focus: stretch for 30s.",
            "You are building momentum, not perfection."
        )

        private fun updateAppWidget(context: Context, appWidgetManager: AppWidgetManager, appWidgetId: Int) {
            val views = RemoteViews(context.packageName, R.layout.widget_study_pulse)
            val message = prompts.random()

            views.setTextViewText(R.id.widget_title, context.getString(R.string.widget_title))
            views.setTextViewText(R.id.widget_message, message)
            views.setTextViewText(R.id.widget_action, context.getString(R.string.widget_cta))

            val intent = Intent(context, MainActivity::class.java)
            val pendingIntent = PendingIntent.getActivity(
                context,
                0,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
            views.setOnClickPendingIntent(R.id.widget_action, pendingIntent)
            views.setOnClickPendingIntent(R.id.widget_message, pendingIntent)

            appWidgetManager.updateAppWidget(appWidgetId, views)
        }
    }
}
