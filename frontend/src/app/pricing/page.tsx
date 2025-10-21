import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Check, Zap, Star, Crown } from 'lucide-react'

const tiers = [
  {
    name: 'Bronze',
    icon: Zap,
    price: 499,
    description: 'Perfect for startups and small teams',
    features: [
      '10,000 executions/month',
      'Basic agent packages',
      'Email support',
      '99.9% uptime SLA',
      'Standard rate limits',
      'Community access',
      'Basic analytics',
      'API access',
    ],
    cta: 'Start Free Trial',
    popular: false,
  },
  {
    name: 'Silver',
    icon: Star,
    price: 1499,
    description: 'For growing businesses with advanced needs',
    features: [
      '50,000 executions/month',
      'All agent packages',
      'Priority email support',
      '99.95% uptime SLA',
      'Increased rate limits',
      'Advanced analytics',
      'Webhook integrations',
      'Custom workflows',
      'Multi-region deployment',
    ],
    cta: 'Start Free Trial',
    popular: false,
  },
  {
    name: 'Gold',
    icon: Crown,
    price: 4999,
    description: 'Enterprise-grade with premium features',
    features: [
      '250,000 executions/month',
      'All agent packages + premium',
      '24/7 priority support',
      '99.99% uptime SLA',
      'Dedicated rate limits',
      'Advanced analytics + BI',
      'Custom integrations',
      'Agent swarms',
      'Multi-modal processing',
      'Federated learning',
      'Dedicated account manager',
      'SLA guarantees',
    ],
    cta: 'Contact Sales',
    popular: true,
  },
  {
    name: 'Platinum',
    icon: Crown,
    price: null,
    description: 'Custom solutions for large enterprises',
    features: [
      'Unlimited executions',
      'All features + custom agents',
      'Dedicated support team',
      '99.999% uptime SLA',
      'No rate limits',
      'White-label options',
      'On-premise deployment',
      'Custom SLA',
      'Dedicated infrastructure',
      'Advanced security features',
      'Custom compliance',
      'Training & onboarding',
    ],
    cta: 'Contact Sales',
    popular: false,
  },
]

const addons = [
  {
    name: 'Additional Executions',
    price: '$0.01 per execution',
    description: 'Pay-as-you-go for usage beyond your plan',
  },
  {
    name: 'Custom Agent Development',
    price: 'Starting at $10,000',
    description: 'Build bespoke agents for your specific use case',
  },
  {
    name: 'Professional Services',
    price: '$250/hour',
    description: 'Expert consultation and implementation support',
  },
  {
    name: 'Extended Support',
    price: '$2,000/month',
    description: '24/7 phone support with 15-minute response time',
  },
]

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="mx-auto max-w-7xl px-6 py-24 lg:px-8">
        {/* Header */}
        <div className="mx-auto max-w-4xl text-center mb-16">
          <Badge className="mb-4">Transparent Pricing</Badge>
          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl mb-4">
            Choose Your Plan
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Scale from startup to enterprise with flexible pricing. All plans include a 14-day free trial.
          </p>
        </div>

        {/* Pricing Tiers */}
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-4 mb-16">
          {tiers.map((tier) => {
            const Icon = tier.icon
            return (
              <Card
                key={tier.name}
                className={`relative p-8 ${
                  tier.popular
                    ? 'ring-2 ring-blue-600 shadow-xl scale-105'
                    : ''
                }`}
              >
                {tier.popular && (
                  <Badge className="absolute -top-3 left-1/2 -translate-x-1/2">
                    Most Popular
                  </Badge>
                )}
                
                <div className="mb-6">
                  <div className="flex items-center gap-2 mb-2">
                    <Icon className="h-6 w-6 text-blue-600" />
                    <h3 className="text-2xl font-bold">{tier.name}</h3>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {tier.description}
                  </p>
                </div>

                <div className="mb-6">
                  {tier.price ? (
                    <>
                      <span className="text-4xl font-bold">${tier.price}</span>
                      <span className="text-gray-600 dark:text-gray-400">/month</span>
                    </>
                  ) : (
                    <span className="text-4xl font-bold">Custom</span>
                  )}
                </div>

                <Button
                  className="w-full mb-6"
                  variant={tier.popular ? 'default' : 'outline'}
                  asChild
                >
                  <Link href={tier.price ? '/signup' : 'https://bizbot.store'}>
                    {tier.cta}
                  </Link>
                </Button>

                <ul className="space-y-3">
                  {tier.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-2">
                      <Check className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>
              </Card>
            )
          })}
        </div>

        {/* Add-ons */}
        <div className="mb-16">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold mb-4">Add-ons & Services</h2>
            <p className="text-lg text-gray-600 dark:text-gray-400">
              Enhance your plan with additional capabilities
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {addons.map((addon) => (
              <Card key={addon.name} className="p-6">
                <h3 className="text-xl font-semibold mb-2">{addon.name}</h3>
                <p className="text-2xl font-bold text-blue-600 mb-2">{addon.price}</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">{addon.description}</p>
              </Card>
            ))}
          </div>
        </div>

        {/* FAQ */}
        <div className="mx-auto max-w-3xl">
          <h2 className="text-3xl font-bold text-center mb-8">Frequently Asked Questions</h2>
          <div className="space-y-6">
            <Card className="p-6">
              <h3 className="font-semibold mb-2">What happens after the free trial?</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                After your 14-day free trial, you'll be automatically enrolled in the plan you selected. You can cancel anytime before the trial ends without being charged.
              </p>
            </Card>

            <Card className="p-6">
              <h3 className="font-semibold mb-2">Can I change plans later?</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately, and we'll prorate the billing accordingly.
              </p>
            </Card>

            <Card className="p-6">
              <h3 className="font-semibold mb-2">What payment methods do you accept?</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                We accept all major credit cards, ACH transfers, and wire transfers for enterprise accounts. All payments are processed securely through Stripe.
              </p>
            </Card>

            <Card className="p-6">
              <h3 className="font-semibold mb-2">Do you offer discounts for annual billing?</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Yes! Save 20% when you pay annually. Contact our sales team for custom enterprise agreements.
              </p>
            </Card>
          </div>
        </div>

        {/* CTA */}
        <div className="mt-16 text-center">
          <Card className="p-12 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20">
            <h2 className="text-3xl font-bold mb-4">Ready to get started?</h2>
            <p className="text-lg text-gray-600 dark:text-gray-400 mb-8">
              Start your 14-day free trial today. No credit card required.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" asChild>
                <Link href="/signup">Start Free Trial</Link>
              </Button>
              <Button size="lg" variant="outline" asChild>
                <Link href="https://bizbot.store" target="_blank">Contact Sales</Link>
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}

