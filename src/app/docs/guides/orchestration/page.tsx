import { GenericDocPage } from '@/components/docs/GenericDocPage'

export default function OrchestrationPage() {
  return (
    <GenericDocPage
      title="Agent Orchestration"
      category="Guides"
      description="Advanced patterns for orchestrating multiple agents in complex workflows"
      content={{
        sections: [
          {
            title: "Overview",
            content: "Agent orchestration enables you to combine multiple agents into sophisticated workflows. Chain agents together, run them in parallel, or create conditional logic based on agent outputs. Our orchestration engine handles execution order, data passing, and error handling."
          },
          {
            title: "Sequential Execution",
            content: (
              <div className="space-y-4">
                <p className="text-gray-700 dark:text-gray-300">
                  Execute agents in sequence, passing output from one to the next:
                </p>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                  <code>{`workflow = client.create_workflow([
    {
        "agent_id": "security-scanner",
        "input": {"target": "https://example.com"}
    },
    {
        "agent_id": "report-generator",
        "input": {"scan_results": "{{previous.output}}"}
    }
])

result = client.execute_workflow(workflow)`}</code>
                </pre>
              </div>
            )
          },
          {
            title: "Parallel Execution",
            content: (
              <div className="space-y-4">
                <p className="text-gray-700 dark:text-gray-300">
                  Run multiple agents concurrently for faster processing:
                </p>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                  <code>{`workflow = client.create_workflow({
    "parallel": [
        {"agent_id": "security-scanner", "input": {...}},
        {"agent_id": "performance-analyzer", "input": {...}},
        {"agent_id": "seo-auditor", "input": {...}}
    ]
})

results = client.execute_workflow(workflow)`}</code>
                </pre>
              </div>
            )
          },
          {
            title: "Conditional Logic",
            content: (
              <div className="space-y-4">
                <p className="text-gray-700 dark:text-gray-300">
                  Add conditional branching based on agent outputs:
                </p>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                  <code>{`workflow = client.create_workflow([
    {"agent_id": "security-scanner", "input": {...}},
    {
        "condition": "{{previous.vulnerabilities.length}} > 0",
        "then": {"agent_id": "incident-responder", "input": {...}},
        "else": {"agent_id": "report-generator", "input": {...}}
    }
])`}</code>
                </pre>
              </div>
            )
          },
          {
            title: "Error Handling",
            content: (
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li>Automatic retries with exponential backoff</li>
                <li>Fallback agents for error scenarios</li>
                <li>Workflow rollback on critical failures</li>
                <li>Detailed error logs and debugging information</li>
              </ul>
            )
          }
        ]
      }}
    />
  )
}

