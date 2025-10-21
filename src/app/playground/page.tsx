'use client'

import { useState, useEffect, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Play, Loader2, CheckCircle, XCircle, Clock, Zap } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

const mockAgents = [
  { id: 'security-scanner', name: 'Security Scanner' },
  { id: 'incident-responder', name: 'Incident Responder' },
  { id: 'ticket-resolver', name: 'Ticket Resolver' },
  { id: 'data-processor', name: 'Data Processor' },
  { id: 'deployment-agent', name: 'Deployment Agent' },
  { id: 'report-generator', name: 'Report Generator' },
  { id: 'audit-agent', name: 'Audit Agent' },
  { id: 'knowledge-base', name: 'Knowledge Base' },
  { id: 'workflow-orchestrator', name: 'Workflow Orchestrator' },
  { id: 'analytics-engine', name: 'Analytics Engine' },
]

const mockScenarios = {
  'security-scanner': {
    title: 'Scan Web Application',
    input: JSON.stringify({
      target_url: 'https://example.com',
      scan_type: 'full',
      include_owasp_top_10: true
    }, null, 2),
    expectedOutput: {
      vulnerabilities_found: 3,
      critical: 0,
      high: 1,
      medium: 2,
      low: 0,
      scan_duration: '2.3s',
      compliance_score: 98.5
    }
  },
  'ticket-resolver': {
    title: 'Classify Support Ticket',
    input: JSON.stringify({
      ticket_id: 'TKT-12345',
      subject: 'Unable to login to dashboard',
      description: 'User reports getting 500 error when trying to access the admin dashboard',
      customer_tier: 'gold'
    }, null, 2),
    expectedOutput: {
      category: 'Technical Issue',
      priority: 'High',
      assigned_team: 'Backend Engineering',
      estimated_resolution: '2 hours',
      suggested_actions: [
        'Check server logs for 500 errors',
        'Verify database connectivity',
        'Review recent deployments'
      ]
    }
  },
  'knowledge-base': {
    title: 'Query Knowledge Base',
    input: JSON.stringify({
      query: 'How do I configure multi-factor authentication?',
      context: 'enterprise_security',
      max_results: 3
    }, null, 2),
    expectedOutput: {
      answer: 'To configure MFA, navigate to Settings > Security > Multi-Factor Authentication...',
      confidence: 0.95,
      sources: [
        'Security Documentation - MFA Setup',
        'Admin Guide - Authentication',
        'Best Practices - Security'
      ],
      related_topics: ['SSO', 'Password Policies', 'Session Management']
    }
  }
}

function PlaygroundContent() {
  const searchParams = useSearchParams()
  const { toast } = useToast()
  
  const [selectedAgent, setSelectedAgent] = useState(searchParams.get('agent') || 'security-scanner')
  const [mode, setMode] = useState<'live' | 'mock'>('mock')
  const [input, setInput] = useState('')
  const [output, setOutput] = useState('')
  const [isExecuting, setIsExecuting] = useState(false)
  const [executionTime, setExecutionTime] = useState<number | null>(null)
  const [executionStatus, setExecutionStatus] = useState<'idle' | 'success' | 'error'>('idle')

  useEffect(() => {
    const scenario = mockScenarios[selectedAgent as keyof typeof mockScenarios]
    if (scenario) {
      setInput(scenario.input)
      setOutput('')
      setExecutionStatus('idle')
      setExecutionTime(null)
    }
  }, [selectedAgent])

  const handleExecute = async () => {
    setIsExecuting(true)
    setExecutionStatus('idle')
    setOutput('')
    
    const startTime = Date.now()

    try {
      if (mode === 'mock') {
        // Simulate execution delay
        await new Promise(resolve => setTimeout(resolve, 1500 + Math.random() * 1000))
        
        const scenario = mockScenarios[selectedAgent as keyof typeof mockScenarios]
        if (scenario) {
          setOutput(JSON.stringify(scenario.expectedOutput, null, 2))
          setExecutionStatus('success')
          setExecutionTime(Date.now() - startTime)
          
          toast({
            title: "Execution Successful",
            description: `Agent executed in ${((Date.now() - startTime) / 1000).toFixed(2)}s`,
          })
        }
      } else {
        // Live mode - call actual API
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/marketplace/agents/execute`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            agent_id: selectedAgent,
            input: JSON.parse(input),
          }),
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        setOutput(JSON.stringify(data, null, 2))
        setExecutionStatus('success')
        setExecutionTime(Date.now() - startTime)
        
        toast({
          title: "Execution Successful",
          description: `Agent executed in ${((Date.now() - startTime) / 1000).toFixed(2)}s`,
        })
      }
    } catch (error) {
      setExecutionStatus('error')
      setOutput(JSON.stringify({
        error: 'Execution failed',
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString()
      }, null, 2))
      
      toast({
        title: "Execution Failed",
        description: error instanceof Error ? error.message : 'Unknown error',
        variant: "destructive",
      })
    } finally {
      setIsExecuting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="mx-auto max-w-7xl px-6 py-12 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-4">Agent Playground</h1>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Test agents in real-time with live execution or explore mock scenarios.
          </p>
        </div>

        {/* Mode Toggle */}
        <Card className="p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="mode-toggle" className="text-base font-semibold">
                Execution Mode
              </Label>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                {mode === 'mock' ? 'Using simulated responses for demonstration' : 'Connected to live API'}
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span className={mode === 'mock' ? 'font-semibold' : 'text-gray-500'}>Mock</span>
              <Switch
                id="mode-toggle"
                checked={mode === 'live'}
                onCheckedChange={(checked) => setMode(checked ? 'live' : 'mock')}
              />
              <span className={mode === 'live' ? 'font-semibold' : 'text-gray-500'}>Live</span>
            </div>
          </div>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Configuration Panel */}
          <div className="lg:col-span-1">
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Configuration</h2>
              
              <div className="space-y-4">
                <div>
                  <Label htmlFor="agent-select">Select Agent</Label>
                  <Select value={selectedAgent} onValueChange={setSelectedAgent}>
                    <SelectTrigger id="agent-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {mockAgents.map((agent) => (
                        <SelectItem key={agent.id} value={agent.id}>
                          {agent.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {mode === 'mock' && mockScenarios[selectedAgent as keyof typeof mockScenarios] && (
                  <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <p className="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-1">
                      Mock Scenario
                    </p>
                    <p className="text-xs text-blue-700 dark:text-blue-300">
                      {mockScenarios[selectedAgent as keyof typeof mockScenarios].title}
                    </p>
                  </div>
                )}

                <Button 
                  onClick={handleExecute} 
                  disabled={isExecuting || !input.trim()}
                  className="w-full"
                  size="lg"
                >
                  {isExecuting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Executing...
                    </>
                  ) : (
                    <>
                      <Play className="mr-2 h-4 w-4" />
                      Execute Agent
                    </>
                  )}
                </Button>

                {executionStatus !== 'idle' && (
                  <div className="space-y-2 pt-4 border-t">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">Status</span>
                      <div className="flex items-center gap-2">
                        {executionStatus === 'success' ? (
                          <>
                            <CheckCircle className="h-4 w-4 text-green-600" />
                            <span className="text-green-600 font-semibold">Success</span>
                          </>
                        ) : (
                          <>
                            <XCircle className="h-4 w-4 text-red-600" />
                            <span className="text-red-600 font-semibold">Failed</span>
                          </>
                        )}
                      </div>
                    </div>
                    {executionTime && (
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600 dark:text-gray-400">Execution Time</span>
                        <div className="flex items-center gap-2">
                          <Clock className="h-4 w-4 text-blue-600" />
                          <span className="font-semibold">{(executionTime / 1000).toFixed(2)}s</span>
                        </div>
                      </div>
                    )}
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">Mode</span>
                      <Badge variant={mode === 'live' ? 'default' : 'secondary'}>
                        {mode === 'live' ? 'Live' : 'Mock'}
                      </Badge>
                    </div>
                  </div>
                )}
              </div>
            </Card>
          </div>

          {/* Input/Output Panel */}
          <div className="lg:col-span-2">
            <Card className="p-6">
              <Tabs defaultValue="input">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="input">Input</TabsTrigger>
                  <TabsTrigger value="output">Output</TabsTrigger>
                </TabsList>
                
                <TabsContent value="input" className="mt-4">
                  <div className="space-y-2">
                    <Label htmlFor="input-json">Request Payload (JSON)</Label>
                    <Textarea
                      id="input-json"
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      placeholder="Enter JSON input..."
                      className="font-mono text-sm min-h-[400px]"
                    />
                  </div>
                </TabsContent>
                
                <TabsContent value="output" className="mt-4">
                  <div className="space-y-2">
                    <Label htmlFor="output-json">Response (JSON)</Label>
                    <Textarea
                      id="output-json"
                      value={output}
                      readOnly
                      placeholder="Execution output will appear here..."
                      className="font-mono text-sm min-h-[400px] bg-gray-50 dark:bg-gray-800"
                    />
                  </div>
                </TabsContent>
              </Tabs>
            </Card>
          </div>
        </div>

        {/* Info Banner */}
        <Card className="mt-6 p-6 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border-blue-200 dark:border-blue-800">
          <div className="flex items-start gap-4">
            <Zap className="h-6 w-6 text-blue-600 flex-shrink-0 mt-1" />
            <div>
              <h3 className="font-semibold text-lg mb-2">Interactive Testing Environment</h3>
              <p className="text-sm text-gray-700 dark:text-gray-300">
                This playground allows you to test all agent capabilities in both mock and live modes. 
                Mock mode uses pre-configured scenarios for instant testing, while live mode connects to the actual API. 
                All executions are logged and can be reviewed in your dashboard.
              </p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}

export default function PlaygroundPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
      <PlaygroundContent />
    </Suspense>
  )
}

