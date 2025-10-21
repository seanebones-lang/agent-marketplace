import { GenericDocPage } from '@/components/docs/GenericDocPage'

export default function KnowledgeBasePage() {
  return (
    <GenericDocPage
      title="Knowledge Base Agent"
      category="Agent Packages"
      description="Intelligent knowledge management with semantic search, automated documentation, and context-aware responses"
      content={{
        sections: [
          {
            title: "Overview",
            content: "The Knowledge Base agent provides intelligent knowledge management capabilities including semantic search, automated documentation generation, and context-aware question answering. It uses RAG (Retrieval Augmented Generation) with vector embeddings for accurate information retrieval."
          },
          {
            title: "Key Features",
            content: (
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li>Semantic search with vector embeddings</li>
                <li>Automated documentation generation</li>
                <li>Context-aware question answering</li>
                <li>Multi-source knowledge aggregation</li>
                <li>Real-time knowledge base updates</li>
                <li>Integration with Confluence, SharePoint, Notion</li>
                <li>99.2% accuracy, sub-second response times</li>
              </ul>
            )
          },
          {
            title: "Usage Example",
            content: (
              <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                <code>{`result = client.execute_agent(
    agent_id="knowledge-base",
    input_data={
        "query": "How do I configure SSL certificates?",
        "sources": ["documentation", "tickets", "runbooks"],
        "max_results": 5
    }
)

print(f"Answer: {result.answer}")
print(f"Sources: {result.sources}")
print(f"Confidence: {result.confidence}")`}</code>
              </pre>
            )
          }
        ]
      }}
    />
  )
}

