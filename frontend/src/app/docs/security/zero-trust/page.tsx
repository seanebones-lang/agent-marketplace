import { GenericDocPage } from '@/components/docs/GenericDocPage'

export default function ZeroTrustPage() {
  return (
    <GenericDocPage
      title="Zero-Trust Architecture"
      category="Security"
      description="Implementation of zero-trust security principles across the Agent Marketplace platform"
      content={{
        sections: [
          {
            title: "Zero-Trust Principles",
            content: "Our zero-trust architecture is built on the principle of 'never trust, always verify.' Every request, whether from inside or outside our network, is authenticated, authorized, and encrypted. We implement micro-segmentation, least-privilege access, and continuous verification."
          },
          {
            title: "Implementation Layers",
            content: (
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li><strong>Identity Verification:</strong> Multi-factor authentication and API key validation</li>
                <li><strong>Device Security:</strong> Device fingerprinting and anomaly detection</li>
                <li><strong>Network Segmentation:</strong> Micro-segmentation with isolated execution environments</li>
                <li><strong>Application Security:</strong> Input validation, output encoding, and CSRF protection</li>
                <li><strong>Data Security:</strong> Encryption at rest and in transit, data classification</li>
                <li><strong>Monitoring:</strong> Real-time threat detection and behavioral analysis</li>
                <li><strong>Policy Enforcement:</strong> Dynamic access control based on context and risk</li>
              </ul>
            )
          },
          {
            title: "Agent Sandboxing",
            content: "Each agent execution runs in an isolated sandbox environment with restricted system access. We use seccomp filters, AppArmor profiles, and resource limits to prevent malicious code execution and ensure agent isolation."
          },
          {
            title: "Continuous Verification",
            content: "Access is continuously verified throughout each session. We monitor for anomalous behavior, enforce session timeouts, and require re-authentication for sensitive operations. All access attempts are logged and analyzed in real-time."
          }
        ]
      }}
    />
  )
}

