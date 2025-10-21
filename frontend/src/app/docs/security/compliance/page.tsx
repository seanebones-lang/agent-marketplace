import { GenericDocPage } from '@/components/docs/GenericDocPage'

export default function CompliancePage() {
  return (
    <GenericDocPage
      title="Compliance"
      category="Security"
      description="Regulatory compliance certifications and standards adherence for enterprise requirements"
      content={{
        sections: [
          {
            title: "Compliance Certifications",
            content: "Agent Marketplace is designed to meet the most stringent compliance requirements for enterprise customers. We maintain readiness for SOC 2 Type II, ISO 27001, and FedRAMP certifications, and are fully compliant with GDPR, CCPA, and HIPAA requirements."
          },
          {
            title: "SOC 2 Type II",
            content: (
              <div className="space-y-3 text-gray-700 dark:text-gray-300">
                <p>Our SOC 2 Type II readiness demonstrates our commitment to:</p>
                <ul className="list-disc pl-6 space-y-1">
                  <li>Security: Protection against unauthorized access</li>
                  <li>Availability: System uptime and performance</li>
                  <li>Processing Integrity: Complete and accurate processing</li>
                  <li>Confidentiality: Protection of sensitive information</li>
                  <li>Privacy: Collection, use, and disclosure practices</li>
                </ul>
              </div>
            )
          },
          {
            title: "GDPR Compliance",
            content: (
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li>Data subject rights (access, rectification, erasure, portability)</li>
                <li>Lawful basis for processing</li>
                <li>Data protection by design and by default</li>
                <li>Data breach notification procedures</li>
                <li>Data Processing Agreements (DPAs) available</li>
                <li>EU data residency options</li>
              </ul>
            )
          },
          {
            title: "HIPAA Readiness",
            content: "For healthcare customers, we provide HIPAA-ready infrastructure including Business Associate Agreements (BAAs), encrypted PHI storage, audit logging, and access controls meeting HIPAA Security Rule requirements."
          },
          {
            title: "Industry Standards",
            content: (
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li>ISO 27001: Information security management</li>
                <li>PCI-DSS: Payment card data security</li>
                <li>NIST Cybersecurity Framework</li>
                <li>CIS Controls</li>
                <li>OWASP Top 10 protection</li>
              </ul>
            )
          }
        ]
      }}
    />
  )
}

