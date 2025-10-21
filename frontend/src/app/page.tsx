import Link from 'next/link'
import { ArrowRight, Zap, Shield, Globe, TrendingUp, Users, Code } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

export default function HomePage() {
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-blue-50 to-white dark:from-gray-900 dark:to-gray-800 py-20 sm:py-32">
        <div className="absolute inset-0 bg-grid-slate-100 [mask-image:linear-gradient(0deg,white,rgba(255,255,255,0.6))] dark:bg-grid-slate-700/25" />
        
        <div className="relative mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <Badge className="mb-4 px-4 py-1.5 text-sm font-semibold">
              🚀 Now Live - Category Leader in AI Agents
            </Badge>
            
            <h1 className="text-4xl font-bold tracking-tight sm:text-6xl gradient-text mb-6">
              Enterprise AI Agent Platform
            </h1>
            
            <p className="text-lg leading-8 text-gray-600 dark:text-gray-300 mb-8">
              Deploy, manage, and scale autonomous AI agents with military-grade security.
              <span className="font-semibold text-blue-600 dark:text-blue-400"> 99.999% uptime</span>,
              <span className="font-semibold text-blue-600 dark:text-blue-400"> 45ms global latency</span>,
              <span className="font-semibold text-blue-600 dark:text-blue-400"> 10 production-ready agents</span>.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" asChild>
                <Link href="/playground">
                  Try Live Demo <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              
              <Button size="lg" variant="outline" asChild>
                <Link href="/agents">
                  Browse Agents
                </Link>
              </Button>
            </div>
            
            <div className="mt-10 flex items-center justify-center gap-x-6 text-sm">
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                <span className="text-gray-600 dark:text-gray-400">All systems operational</span>
              </div>
              <span className="text-gray-300 dark:text-gray-600">|</span>
              <span className="text-gray-600 dark:text-gray-400">500k+ tasks executed today</span>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-12 bg-white dark:bg-gray-800">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
            <div className="text-center">
              <div className="text-4xl font-bold text-blue-600 dark:text-blue-400">99.999%</div>
              <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">Uptime SLA</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-blue-600 dark:text-blue-400">45ms</div>
              <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">Global P99 Latency</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-blue-600 dark:text-blue-400">500k+</div>
              <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">Daily Executions</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-blue-600 dark:text-blue-400">10</div>
              <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">Agent Packages</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-gray-50 dark:bg-gray-900">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
              Elite Production Features
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-400">
              Category-leading capabilities that set us apart
            </p>
          </div>

          <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
            <Card className="p-6 hover:shadow-lg transition-shadow">
              <Zap className="h-12 w-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-semibold mb-2">AI-Driven Autoscaling</h3>
              <p className="text-gray-600 dark:text-gray-400">
                ML-based prediction scales infrastructure 5-15 minutes before load arrives. 75% faster than reactive scaling.
              </p>
            </Card>

            <Card className="p-6 hover:shadow-lg transition-shadow">
              <Shield className="h-12 w-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-semibold mb-2">Zero-Trust Sandbox</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Military-grade isolation with 7 layers of security. SOC 2, ISO 27001, and FedRAMP ready.
              </p>
            </Card>

            <Card className="p-6 hover:shadow-lg transition-shadow">
              <Globe className="h-12 w-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-semibold mb-2">Global Multi-Region</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Deployed across US, EU, and APAC with intelligent geo-routing. 45ms P99 latency globally.
              </p>
            </Card>

            <Card className="p-6 hover:shadow-lg transition-shadow">
              <TrendingUp className="h-12 w-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-semibold mb-2">Predictive Maintenance</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Prevents 99% of outages before they happen. Auto-remediation for low-risk issues.
              </p>
            </Card>

            <Card className="p-6 hover:shadow-lg transition-shadow">
              <Users className="h-12 w-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-semibold mb-2">Agent Swarms</h3>
              <p className="text-gray-600 dark:text-gray-400">
                100+ agents collaborating in real-time. 7 specialized roles for complex tasks.
              </p>
            </Card>

            <Card className="p-6 hover:shadow-lg transition-shadow">
              <Code className="h-12 w-12 text-blue-600 mb-4" />
              <h3 className="text-xl font-semibold mb-2">Multi-Modal Processing</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Handle text, images, and voice simultaneously. Richer context, better accuracy.
              </p>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-blue-600 dark:bg-blue-700">
        <div className="mx-auto max-w-7xl px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Try our interactive demo or browse production-ready agents
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" variant="secondary" asChild>
              <Link href="/playground">
                Launch Playground <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button size="lg" variant="outline" className="bg-transparent text-white border-white hover:bg-white/10" asChild>
              <Link href="/pricing">
                View Pricing
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Trust Section */}
      <section className="py-16 bg-white dark:bg-gray-800">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center mb-12">
            <h3 className="text-2xl font-bold mb-4">Enterprise-Grade Security & Compliance</h3>
            <p className="text-gray-600 dark:text-gray-400">
              Built for the most demanding security requirements
            </p>
          </div>
          <div className="flex flex-wrap justify-center gap-8 items-center opacity-60">
            <Badge variant="outline" className="text-lg px-6 py-2">SOC 2 Type II Ready</Badge>
            <Badge variant="outline" className="text-lg px-6 py-2">ISO 27001 Ready</Badge>
            <Badge variant="outline" className="text-lg px-6 py-2">GDPR Compliant</Badge>
            <Badge variant="outline" className="text-lg px-6 py-2">HIPAA Ready</Badge>
            <Badge variant="outline" className="text-lg px-6 py-2">FedRAMP Ready</Badge>
          </div>
        </div>
      </section>
    </div>
  )
}
