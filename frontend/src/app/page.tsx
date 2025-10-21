export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Agent Marketplace Platform
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Enterprise Agentic AI Platform - Rent autonomous agents for enterprise operations
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-2xl font-semibold mb-3">Customer Support</h3>
              <p className="text-gray-600">
                Autonomous ticket resolution, knowledge base search, and smart escalation
              </p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-2xl font-semibold mb-3">Operations</h3>
              <p className="text-gray-600">
                ETL automation, report generation, and workflow orchestration
              </p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-2xl font-semibold mb-3">DevOps & Security</h3>
              <p className="text-gray-600">
                Incident response, deployment automation, and security scanning
              </p>
            </div>
          </div>
          
          <div className="mt-12">
            <a
              href="/api/v1/packages"
              className="bg-blue-600 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-blue-700 transition"
            >
              View API Documentation
            </a>
          </div>
        </div>
      </div>
    </main>
  );
}

