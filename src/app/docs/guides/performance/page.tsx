import { GenericDocPage } from '@/components/docs/GenericDocPage'

export default function PerformancePage() {
  return (
    <GenericDocPage
      title="Performance Optimization"
      category="Guides"
      description="Best practices for optimizing agent execution speed, cost, and reliability"
      content={{
        sections: [
          {
            title: "Caching Strategies",
            content: (
              <div className="space-y-3 text-gray-700 dark:text-gray-300">
                <p>Implement intelligent caching to reduce costs and improve response times:</p>
                <ul className="list-disc pl-6 space-y-1">
                  <li>Cache agent results for identical inputs (TTL: 1-24 hours)</li>
                  <li>Use semantic caching for similar queries</li>
                  <li>Implement client-side caching for frequently accessed data</li>
                  <li>Leverage our built-in Redis caching layer</li>
                </ul>
              </div>
            )
          },
          {
            title: "Batch Processing",
            content: (
              <div className="space-y-4">
                <p className="text-gray-700 dark:text-gray-300">
                  Process multiple items in a single request:
                </p>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                  <code>{`result = client.batch_execute(
    agent_id="security-scanner",
    batch_input=[
        {"target": "https://site1.com"},
        {"target": "https://site2.com"},
        {"target": "https://site3.com"}
    ]
)

# 75% faster than individual requests`}</code>
                </pre>
              </div>
            )
          },
          {
            title: "Async Execution",
            content: (
              <div className="space-y-4">
                <p className="text-gray-700 dark:text-gray-300">
                  Use async execution for long-running agents:
                </p>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                  <code>{`# Start async execution
execution = client.execute_agent_async(
    agent_id="data-processor",
    input_data={...}
)

# Check status later
status = client.get_execution_status(execution.id)

# Or use webhooks for notifications
client.set_webhook(
    execution_id=execution.id,
    webhook_url="https://your-app.com/webhook"
)`}</code>
                </pre>
              </div>
            )
          },
          {
            title: "Cost Optimization",
            content: (
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li>Use quick scan modes for non-critical checks</li>
                <li>Implement request deduplication</li>
                <li>Set appropriate timeout values</li>
                <li>Monitor usage with our analytics dashboard</li>
                <li>Use reserved capacity for predictable workloads (40% savings)</li>
              </ul>
            )
          },
          {
            title: "Performance Monitoring",
            content: "Track agent performance metrics including execution time, success rate, and cost per execution. Set up alerts for performance degradation and use our AI-driven recommendations for optimization."
          }
        ]
      }}
    />
  )
}

