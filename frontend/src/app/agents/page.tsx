'use client';

import { useState } from 'react';
import { useAgents, useCategories } from '@/hooks/useAgents';
import { AgentCard } from '@/components/features/AgentCard';
import { Button } from '@/components/ui/Button';

export default function AgentsPage() {
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>();
  const { packages, loading: packagesLoading } = useAgents(selectedCategory);
  const { categories, loading: categoriesLoading } = useCategories();

  if (packagesLoading || categoriesLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading agents...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Agent Marketplace
          </h1>
          <p className="text-xl text-gray-600">
            Browse and deploy autonomous AI agents for your enterprise
          </p>
        </div>

        {/* Category Filter */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-2">
            <Button
              variant={!selectedCategory ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setSelectedCategory(undefined)}
            >
              All Agents
            </Button>
            {categories.map((category) => (
              <Button
                key={category.id}
                variant={selectedCategory === category.id ? 'primary' : 'outline'}
                size="sm"
                onClick={() => setSelectedCategory(category.id)}
              >
                {category.name}
              </Button>
            ))}
          </div>
        </div>

        {/* Agent Grid */}
        {packages.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600 text-lg">No agents found</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {packages.map((agent) => (
              <AgentCard key={agent.package_id} agent={agent} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

