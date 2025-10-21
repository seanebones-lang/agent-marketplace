/**
 * TanStack Query Client Configuration
 * Optimized for performance with intelligent caching and retry strategies
 */

import { QueryClient, QueryCache, MutationCache } from '@tanstack/react-query';

// Create query cache with error handling
const queryCache = new QueryCache({
  onError: (error, query) => {
    console.error(`Query error for ${query.queryHash}:`, error);
    
    // Log to monitoring service in production
    if (process.env.NODE_ENV === 'production') {
      // TODO: Send to monitoring service (e.g., Sentry)
    }
  },
  onSuccess: (data, query) => {
    console.debug(`Query success for ${query.queryHash}`);
  }
});

// Create mutation cache with error handling
const mutationCache = new MutationCache({
  onError: (error, variables, context, mutation) => {
    console.error(`Mutation error:`, error);
    
    // Log to monitoring service in production
    if (process.env.NODE_ENV === 'production') {
      // TODO: Send to monitoring service
    }
  }
});

// Create optimized query client
export const queryClient = new QueryClient({
  queryCache,
  mutationCache,
  defaultOptions: {
    queries: {
      // Caching strategy
      staleTime: 5 * 60 * 1000, // 5 minutes - data considered fresh
      gcTime: 10 * 60 * 1000, // 10 minutes - cache retention (formerly cacheTime)
      
      // Retry strategy
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors (client errors)
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false;
        }
        
        // Don't retry on rate limit errors
        if (error?.response?.status === 429) {
          return false;
        }
        
        // Don't retry on authentication errors
        if (error?.response?.status === 401 || error?.response?.status === 403) {
          return false;
        }
        
        // Retry up to 3 times for server errors
        return failureCount < 3;
      },
      retryDelay: (attemptIndex) => {
        // Exponential backoff: 1s, 2s, 4s
        return Math.min(1000 * 2 ** attemptIndex, 30000);
      },
      
      // Refetch configuration
      refetchOnWindowFocus: false, // Don't refetch on window focus (can be enabled per-query)
      refetchOnReconnect: true, // Refetch when network reconnects
      refetchOnMount: true, // Refetch when component mounts
      
      // Network mode
      networkMode: 'online', // Only fetch when online
      
      // Error handling
      throwOnError: false, // Handle errors locally by default (formerly useErrorBoundary)
    },
    mutations: {
      // Retry strategy for mutations
      retry: (failureCount, error: any) => {
        // Never retry mutations by default (can be overridden per-mutation)
        return false;
      },
      
      // Network mode
      networkMode: 'online',
      
      // Error handling
      throwOnError: false, // Handle errors locally (formerly useErrorBoundary)
    }
  }
});

// Query key factories for consistent cache management
export const queryKeys = {
  // Agent packages
  packages: {
    all: ['packages'] as const,
    lists: () => [...queryKeys.packages.all, 'list'] as const,
    list: (filters?: Record<string, any>) => 
      [...queryKeys.packages.lists(), filters] as const,
    details: () => [...queryKeys.packages.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.packages.details(), id] as const,
  },
  
  // Agent executions
  executions: {
    all: ['executions'] as const,
    lists: () => [...queryKeys.executions.all, 'list'] as const,
    list: (filters?: Record<string, any>) => 
      [...queryKeys.executions.lists(), filters] as const,
    details: () => [...queryKeys.executions.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.executions.details(), id] as const,
  },
  
  // Analytics
  analytics: {
    all: ['analytics'] as const,
    overview: () => [...queryKeys.analytics.all, 'overview'] as const,
    dashboard: () => [...queryKeys.analytics.all, 'dashboard'] as const,
    timeseries: (metric: string, filters?: Record<string, any>) =>
      [...queryKeys.analytics.all, 'timeseries', metric, filters] as const,
  },
  
  // User/Customer
  user: {
    all: ['user'] as const,
    current: () => [...queryKeys.user.all, 'current'] as const,
    subscription: () => [...queryKeys.user.all, 'subscription'] as const,
    usage: () => [...queryKeys.user.all, 'usage'] as const,
  },
  
  // Billing
  billing: {
    all: ['billing'] as const,
    invoices: () => [...queryKeys.billing.all, 'invoices'] as const,
    paymentMethods: () => [...queryKeys.billing.all, 'payment-methods'] as const,
  }
};

// Cache invalidation helpers
export const invalidateQueries = {
  packages: () => queryClient.invalidateQueries({ queryKey: queryKeys.packages.all }),
  executions: () => queryClient.invalidateQueries({ queryKey: queryKeys.executions.all }),
  analytics: () => queryClient.invalidateQueries({ queryKey: queryKeys.analytics.all }),
  user: () => queryClient.invalidateQueries({ queryKey: queryKeys.user.all }),
  billing: () => queryClient.invalidateQueries({ queryKey: queryKeys.billing.all }),
  all: () => queryClient.invalidateQueries(),
};

// Prefetch helpers
export const prefetchQueries = {
  packages: async () => {
    // TODO: Import API client and prefetch
    // await queryClient.prefetchQuery({
    //   queryKey: queryKeys.packages.lists(),
    //   queryFn: () => apiClient.getPackages()
    // });
  },
  
  dashboard: async () => {
    // Prefetch dashboard data
    // await Promise.all([
    //   queryClient.prefetchQuery({
    //     queryKey: queryKeys.analytics.overview(),
    //     queryFn: () => apiClient.getAnalyticsOverview()
    //   }),
    //   queryClient.prefetchQuery({
    //     queryKey: queryKeys.user.current(),
    //     queryFn: () => apiClient.getCurrentUser()
    //   })
    // ]);
  }
};

// Performance monitoring
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
  // Log cache statistics in development
  setInterval(() => {
    const cacheStats = {
      queries: queryClient.getQueryCache().getAll().length,
      mutations: queryClient.getMutationCache().getAll().length,
    };
    console.debug('Query cache stats:', cacheStats);
  }, 60000); // Every minute
}

export default queryClient;

