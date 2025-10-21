import { GenericDocPage } from '@/components/docs/GenericDocPage'

export default function WebSocketAPIPage() {
  return (
    <GenericDocPage
      title="WebSocket API"
      category="API Reference"
      description="Real-time bidirectional communication for agent execution monitoring and live updates"
      content={{
        sections: [
          {
            title: "Connection",
            content: (
              <div className="space-y-4">
                <p className="text-gray-700 dark:text-gray-300">
                  Connect to the WebSocket endpoint for real-time updates:
                </p>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                  <code>{`wss://api.agentmarketplace.com/v1/ws?token=YOUR_JWT_TOKEN`}</code>
                </pre>
              </div>
            )
          },
          {
            title: "Authentication",
            content: (
              <div className="space-y-4">
                <p className="text-gray-700 dark:text-gray-300">
                  WebSocket connections require a JWT token. Obtain one from the /auth/token endpoint:
                </p>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                  <code>{`POST /v1/auth/token
Content-Type: application/json

{
  "api_key": "YOUR_API_KEY",
  "expires_in": 3600
}`}</code>
                </pre>
              </div>
            )
          },
          {
            title: "Message Format",
            content: (
              <div className="space-y-4">
                <p className="text-gray-700 dark:text-gray-300">
                  All messages are JSON-formatted:
                </p>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                  <code>{`// Subscribe to execution updates
{
  "type": "subscribe",
  "channel": "execution",
  "execution_id": "exec_abc123"
}

// Execution status update
{
  "type": "execution_update",
  "execution_id": "exec_abc123",
  "status": "processing",
  "progress": 45,
  "timestamp": "2025-10-21T10:00:00Z"
}`}</code>
                </pre>
              </div>
            )
          },
          {
            title: "JavaScript Example",
            content: (
              <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                <code>{`const ws = new WebSocket('wss://api.agentmarketplace.com/v1/ws?token=YOUR_JWT');

ws.onopen = () => {
  // Subscribe to execution updates
  ws.send(JSON.stringify({
    type: 'subscribe',
    channel: 'execution',
    execution_id: 'exec_abc123'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
};`}</code>
              </pre>
            )
          }
        ]
      }}
    />
  )
}

