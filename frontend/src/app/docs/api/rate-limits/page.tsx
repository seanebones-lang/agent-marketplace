import { GenericDocPage } from '@/components/docs/GenericDocPage'

export default function RateLimitsPage() {
  return (
    <GenericDocPage
      title="Rate Limits"
      category="API Reference"
      description="API rate limiting policies, quotas, and best practices for optimal performance"
      content={{
        sections: [
          {
            title: "Rate Limit Tiers",
            content: (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="border-b border-gray-200 dark:border-gray-700">
                    <tr>
                      <th className="py-3 px-4">Tier</th>
                      <th className="py-3 px-4">Requests/Hour</th>
                      <th className="py-3 px-4">Burst Limit</th>
                      <th className="py-3 px-4">Concurrent Executions</th>
                    </tr>
                  </thead>
                  <tbody className="text-gray-700 dark:text-gray-300">
                    <tr className="border-b border-gray-200 dark:border-gray-700">
                      <td className="py-3 px-4 font-semibold">Free</td>
                      <td className="py-3 px-4">100</td>
                      <td className="py-3 px-4">10/min</td>
                      <td className="py-3 px-4">2</td>
                    </tr>
                    <tr className="border-b border-gray-200 dark:border-gray-700">
                      <td className="py-3 px-4 font-semibold">Pro</td>
                      <td className="py-3 px-4">1,000</td>
                      <td className="py-3 px-4">100/min</td>
                      <td className="py-3 px-4">10</td>
                    </tr>
                    <tr className="border-b border-gray-200 dark:border-gray-700">
                      <td className="py-3 px-4 font-semibold">Enterprise</td>
                      <td className="py-3 px-4">Custom</td>
                      <td className="py-3 px-4">Custom</td>
                      <td className="py-3 px-4">Unlimited</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            )
          },
          {
            title: "Rate Limit Headers",
            content: (
              <div className="space-y-4">
                <p className="text-gray-700 dark:text-gray-300">
                  All API responses include rate limit information in headers:
                </p>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                  <code>{`X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1634825600`}</code>
                </pre>
              </div>
            )
          },
          {
            title: "Handling Rate Limits",
            content: (
              <div className="space-y-4">
                <p className="text-gray-700 dark:text-gray-300">
                  When you exceed rate limits, you'll receive a 429 status code:
                </p>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                  <code>{`HTTP/1.1 429 Too Many Requests
Retry-After: 60

{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Please retry after 60 seconds."
  }
}`}</code>
                </pre>
              </div>
            )
          },
          {
            title: "Best Practices",
            content: (
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li>Implement exponential backoff for retries</li>
                <li>Cache responses when possible</li>
                <li>Use batch endpoints for multiple operations</li>
                <li>Monitor rate limit headers proactively</li>
                <li>Spread requests evenly over time</li>
                <li>Contact support for Enterprise tier custom limits</li>
              </ul>
            )
          }
        ]
      }}
    />
  )
}

