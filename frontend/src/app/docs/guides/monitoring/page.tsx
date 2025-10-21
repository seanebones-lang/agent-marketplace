import { GenericDocPage } from '@/components/docs/GenericDocPage'

export default function MonitoringPage() {
  return (
    <GenericDocPage
      title="Monitoring & Logging"
      category="Guides"
      description="Comprehensive monitoring, logging, and observability for agent operations"
      content={{
        sections: [
          {
            title: "Real-Time Monitoring",
            content: "Monitor agent executions in real-time through our dashboard or API. Track success rates, execution times, error rates, and resource usage. Set up custom alerts for anomalies and performance degradation."
          },
          {
            title: "Execution Logs",
            content: (
              <div className="space-y-4">
                <p className="text-gray-700 dark:text-gray-300">
                  Access detailed execution logs for debugging:
                </p>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                  <code>{`logs = client.get_execution_logs(
    execution_id="exec_abc123",
    level="debug"  # debug, info, warn, error
)

for log in logs:
    print(f"[{log.timestamp}] {log.level}: {log.message}")`}</code>
                </pre>
              </div>
            )
          },
          {
            title: "Metrics & Analytics",
            content: (
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li><strong>Performance Metrics:</strong> P50, P95, P99 latencies</li>
                <li><strong>Success Rates:</strong> By agent, time period, and customer</li>
                <li><strong>Error Analysis:</strong> Error types, frequency, and trends</li>
                <li><strong>Cost Tracking:</strong> Spend by agent and time period</li>
                <li><strong>Usage Patterns:</strong> Peak times, popular agents, trends</li>
              </ul>
            )
          },
          {
            title: "Distributed Tracing",
            content: "We use OpenTelemetry for distributed tracing across agent executions. View complete request traces including API calls, agent processing, and external integrations. Identify bottlenecks and optimize performance."
          },
          {
            title: "Alerting",
            content: (
              <div className="space-y-4">
                <p className="text-gray-700 dark:text-gray-300">
                  Configure alerts for critical events:
                </p>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                  <code>{`client.create_alert(
    name="High Error Rate",
    condition="error_rate > 5%",
    window="5m",
    channels=["email", "slack", "pagerduty"]
)`}</code>
                </pre>
              </div>
            )
          },
          {
            title: "Integration Options",
            content: (
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li>Datadog, New Relic, Grafana integration</li>
                <li>Slack, PagerDuty, Opsgenie notifications</li>
                <li>Custom webhooks for real-time events</li>
                <li>Prometheus metrics export</li>
                <li>CloudWatch, Stackdriver logging</li>
              </ul>
            )
          }
        ]
      }}
    />
  )
}

