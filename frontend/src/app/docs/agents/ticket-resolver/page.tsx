import { GenericDocPage } from '@/components/docs/GenericDocPage'

export default function TicketResolverPage() {
  return (
    <GenericDocPage
      title="Ticket Resolver"
      category="Agent Packages"
      description="Automated ticket classification, prioritization, and resolution with ML-powered insights"
      content={{
        sections: [
          {
            title: "Overview",
            content: "The Ticket Resolver agent automates customer support ticket handling with intelligent classification, priority scoring, smart routing, and automated resolution suggestions. It learns from historical tickets to improve accuracy over time."
          },
          {
            title: "Key Features",
            content: (
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li>Automatic ticket classification and categorization</li>
                <li>ML-powered priority scoring</li>
                <li>Smart routing to appropriate teams</li>
                <li>Automated resolution suggestions</li>
                <li>Integration with Zendesk, Jira, Freshdesk</li>
                <li>Sentiment analysis and customer satisfaction prediction</li>
                <li>98.9% success rate, 1.2s average response time</li>
              </ul>
            )
          },
          {
            title: "Usage Example",
            content: (
              <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                <code>{`result = client.execute_agent(
    agent_id="ticket-resolver",
    input_data={
        "ticket_id": "TKT-67890",
        "subject": "Cannot login to account",
        "description": "User reports error when logging in",
        "auto_resolve": True
    }
)

print(f"Category: {result.category}")
print(f"Priority: {result.priority}")
print(f"Suggested Resolution: {result.resolution}")`}</code>
              </pre>
            )
          }
        ]
      }}
    />
  )
}

