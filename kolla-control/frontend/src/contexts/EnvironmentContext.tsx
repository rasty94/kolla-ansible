import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useQuery } from '@tanstack/react-query';

interface Environment {
  id: number;
  name: string;
  description: string;
  config_path: string;
  inventory_path: string;
}

interface EnvironmentContextType {
  currentEnvironment: Environment | null;
  environments: Environment[];
  setEnvironment: (env: Environment) => void;
  isLoading: boolean;
}

const EnvironmentContext = createContext<EnvironmentContextType | undefined>(undefined);

export const EnvironmentProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentEnvironment, setCurrentEnvironment] = useState<Environment | null>(null);

  // Fetch environments
  const { data: environments = [], isLoading } = useQuery<Environment[]>({
    queryKey: ['environments'],
    queryFn: async () => {
      const response = await fetch('/api/v1/environments');
      if (!response.ok) throw new Error('Failed to fetch environments');
      return response.json();
    },
  });

  // Set default environment
  useEffect(() => {
    if (environments.length > 0 && !currentEnvironment) {
      // Try to recover from local storage
      const storedEnvId = localStorage.getItem('selectedEnvironmentId');
      if (storedEnvId) {
        const found = environments.find(e => e.id === parseInt(storedEnvId));
        if (found) {
          setCurrentEnvironment(found);
          return;
        }
      }
      // Default to first
      setCurrentEnvironment(environments[0]);
    }
  }, [environments, currentEnvironment]);

  const setEnvironment = (env: Environment) => {
    setCurrentEnvironment(env);
    localStorage.setItem('selectedEnvironmentId', env.id.toString());
  };

  return (
    <EnvironmentContext.Provider value={{ currentEnvironment, environments, setEnvironment, isLoading }}>
      {children}
    </EnvironmentContext.Provider>
  );
};

export const useEnvironment = () => {
  const context = useContext(EnvironmentContext);
  if (context === undefined) {
    throw new Error('useEnvironment must be used within an EnvironmentProvider');
  }
  return context;
};
