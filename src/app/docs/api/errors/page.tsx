import { GenericDocPage } from '@/components/docs/GenericDocPage'

export default function ErrorHandlingPage() {
  return (
    <GenericDocPage
      title="Error Handling"
      category="API Reference"
      description="Comprehensive error codes, formats, and handling strategies for robust API integration"
      content={{
        sections: [
          {
            title: "HTTP Status Codes",
            content: (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="border-b border-gray-200 dark:border-gray-700">
                    <tr>
                      <th className="py-3 px-4">Code</th>
                      <th className="py-3 px-4">Meaning</th>
                      <th className="py-3 px-4">Description</th>
                    </tr>
                  </thead>
                  <tbody className="text-gray-700 dark:text-gray-300">
                    <tr className="border-b border-gray-200 dark:border-gray-700">
                      <td className="py-3 px-4 font-mono">200</td>
                      <td className="py-3 px-4 font-semibold">OK</td>
                      <td className="py-3 px-4">Request succeeded</td>
                    </tr>
                    <tr className="border-b border-gray-200 dark:border-gray-700">
                      <td className="py-3 px-4 font-mono">400</td>
                      <td className="py-3 px-4 font-semibold">Bad Request</td>
                      <td className="py-3 px-4">Invalid request parameters</td>
                    </tr>
                    <tr className="border-b border-gray-200 dark:border-gray-700">
                      <td className="py-3 px-4 font-mono">401</td>
                      <td className="py-3 px-4 font-semibold">Unauthorized</td>
                      <td className="py-3 px-4">Invalid or missing API key</td>
                    </tr>
                    <tr className="border-b border-gray-200 dark:border-gray-700">
                      <td className="py-3 px-4 font-mono">403</td>
                      <td className="py-3 px-4 font-semibold">Forbidden</td>
                      <td className="py-3 px-4">Insufficient permissions</td>
                    </tr>
                    <tr className="border-b border-gray-200 dark:border-gray-700">
                      <td className="py-3 px-4 font-mono">404</td>
                      <td className="py-3 px-4 font-semibold">Not Found</td>
                      <td className="py-3 px-4">Resource not found</td>
                    </tr>
                    <tr className="border-b border-gray-200 dark:border-gray-700">
                      <td className="py-3 px-4 font-mono">429</td>
                      <td className="py-3 px-4 font-semibold">Too Many Requests</td>
                      <td className="py-3 px-4">Rate limit exceeded</td>
                    </tr>
                    <tr className="border-b border-gray-200 dark:border-gray-700">
                      <td className="py-3 px-4 font-mono">500</td>
                      <td className="py-3 px-4 font-semibold">Internal Server Error</td>
                      <td className="py-3 px-4">Server error occurred</td>
                    </tr>
                    <tr>
                      <td className="py-3 px-4 font-mono">503</td>
                      <td className="py-3 px-4 font-semibold">Service Unavailable</td>
                      <td className="py-3 px-4">Service temporarily unavailable</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            )
          },
          {
            title: "Error Response Format",
            content: (
              <div className="space-y-4">
                <p className="text-gray-700 dark:text-gray-300">
                  All errors follow a consistent JSON format:
                </p>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                  <code>{`{
  "error": {
    "code": "invalid_input",
    "message": "The 'target' field is required",
    "details": {
      "field": "target",
      "reason": "missing_required_field"
    },
    "request_id": "req_abc123"
  }
}`}</code>
                </pre>
              </div>
            )
          },
          {
            title: "Common Error Codes",
            content: (
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li><code className="bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded">invalid_input</code> - Invalid request parameters</li>
                <li><code className="bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded">authentication_failed</code> - Invalid API key</li>
                <li><code className="bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded">rate_limit_exceeded</code> - Too many requests</li>
                <li><code className="bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded">agent_not_found</code> - Agent ID doesn't exist</li>
                <li><code className="bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded">execution_failed</code> - Agent execution error</li>
                <li><code className="bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded">insufficient_credits</code> - Account balance too low</li>
              </ul>
            )
          },
          {
            title: "Error Handling Example",
            content: (
              <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                <code>{`try:
    result = client.execute_agent(
        agent_id="security-scanner",
        input_data={"target": "https://example.com"}
    )
except AgentMarketplaceError as e:
    if e.code == "rate_limit_exceeded":
        # Wait and retry
        time.sleep(int(e.retry_after))
        result = client.execute_agent(...)
    elif e.code == "invalid_input":
        # Fix input and retry
        print(f"Invalid input: {e.details}")
    else:
        # Log and alert
        logger.error(f"Execution failed: {e.message}")`}</code>
              </pre>
            )
          }
        ]
      }}
    />
  )
}

