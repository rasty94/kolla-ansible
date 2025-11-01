import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Play,
  RefreshCw,
  Trash2,
  Download,
  Upload,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  Terminal,
  Clock,
  X,
} from 'lucide-react';
import toast from 'react-hot-toast';

interface Operation {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  dangerous?: boolean;
  command: string;
}

interface OperationExecution {
  id: number;
  operation: string;
  status: 'pending' | 'running' | 'success' | 'failed';
  started_at: string;
  completed_at?: string;
  output?: string;
  error?: string;
}

const OPERATIONS: Operation[] = [
  {
    id: 'deploy',
    name: 'Deploy',
    description: 'Desplegar todos los servicios de OpenStack',
    icon: Play,
    color: 'blue',
    command: 'kolla-ansible deploy',
  },
  {
    id: 'reconfigure',
    name: 'Reconfigure',
    description: 'Reconfigurar servicios sin reiniciarlos',
    icon: RefreshCw,
    color: 'green',
    command: 'kolla-ansible reconfigure',
  },
  {
    id: 'upgrade',
    name: 'Upgrade',
    description: 'Actualizar servicios a nueva versión',
    icon: Upload,
    color: 'purple',
    command: 'kolla-ansible upgrade',
  },
  {
    id: 'stop',
    name: 'Stop',
    description: 'Detener todos los servicios',
    icon: AlertTriangle,
    color: 'orange',
    dangerous: true,
    command: 'kolla-ansible stop',
  },
  {
    id: 'destroy',
    name: 'Destroy',
    description: 'Eliminar todos los contenedores y volúmenes',
    icon: Trash2,
    color: 'red',
    dangerous: true,
    command: 'kolla-ansible destroy',
  },
  {
    id: 'pull',
    name: 'Pull Images',
    description: 'Descargar imágenes Docker más recientes',
    icon: Download,
    color: 'indigo',
    command: 'kolla-ansible pull',
  },
  {
    id: 'backup',
    name: 'Backup',
    description: 'Crear backup de configuraciones y datos',
    icon: CheckCircle2,
    color: 'teal',
    command: 'kolla-ansible mariadb_backup',
  },
];

const OperationsPanel: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedOperation, setSelectedOperation] = useState<Operation | null>(null);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [showOutputModal, setShowOutputModal] = useState(false);
  const [selectedExecution, setSelectedExecution] = useState<OperationExecution | null>(null);

  // Fetch operation history
  const { data: executions = [], isLoading } = useQuery<OperationExecution[]>({
    queryKey: ['operations'],
    queryFn: async () => {
      const response = await fetch('/api/operations');
      if (!response.ok) throw new Error('Error al cargar operaciones');
      return response.json();
    },
    refetchInterval: 5000, // Refetch cada 5 segundos para actualizar estados
  });

  // Execute operation mutation
  const executeMutation = useMutation({
    mutationFn: async (operation: Operation) => {
      const response = await fetch('/api/operations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          operation: operation.id,
          command: operation.command,
        }),
      });
      if (!response.ok) throw new Error('Error al ejecutar operación');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['operations'] });
      toast.success('Operación iniciada exitosamente');
      setShowConfirmModal(false);
      setSelectedOperation(null);
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  const handleOperationClick = (operation: Operation) => {
    setSelectedOperation(operation);
    setShowConfirmModal(true);
  };

  const handleConfirmExecution = () => {
    if (selectedOperation) {
      executeMutation.mutate(selectedOperation);
    }
  };

  const handleViewOutput = (execution: OperationExecution) => {
    setSelectedExecution(execution);
    setShowOutputModal(true);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'text-gray-600 bg-gray-100 dark:bg-gray-700 dark:text-gray-300';
      case 'running':
        return 'text-blue-600 bg-blue-100 dark:bg-blue-900/30 dark:text-blue-300';
      case 'success':
        return 'text-green-600 bg-green-100 dark:bg-green-900/30 dark:text-green-300';
      case 'failed':
        return 'text-red-600 bg-red-100 dark:bg-red-900/30 dark:text-red-300';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-4 h-4" />;
      case 'running':
        return <Loader2 className="w-4 h-4 animate-spin" />;
      case 'success':
        return <CheckCircle2 className="w-4 h-4" />;
      case 'failed':
        return <AlertTriangle className="w-4 h-4" />;
      default:
        return null;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('es-ES');
  };

  const calculateDuration = (start: string, end?: string) => {
    const startTime = new Date(start).getTime();
    const endTime = end ? new Date(end).getTime() : Date.now();
    const duration = Math.floor((endTime - startTime) / 1000);
    return `${Math.floor(duration / 60)}m ${duration % 60}s`;
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Operations Panel
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Ejecuta operaciones de Kolla-Ansible en tu infraestructura
        </p>
      </div>

      {/* Operations Grid */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Operaciones Disponibles
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {OPERATIONS.map((operation) => {
            const Icon = operation.icon;
            return (
              <button
                key={operation.id}
                onClick={() => handleOperationClick(operation)}
                className={`
                  p-6 rounded-lg border-2 transition-all text-left
                  ${
                    operation.dangerous
                      ? 'border-red-300 dark:border-red-800 hover:border-red-500 dark:hover:border-red-600 bg-red-50 dark:bg-red-900/10'
                      : 'border-gray-300 dark:border-gray-600 hover:border-blue-500 dark:hover:border-blue-400 bg-white dark:bg-gray-800'
                  }
                  hover:shadow-lg
                `}
              >
                <div className="flex items-start justify-between mb-3">
                  <div
                    className={`
                      p-3 rounded-lg
                      bg-${operation.color}-100 dark:bg-${operation.color}-900/30
                    `}
                  >
                    <Icon
                      className={`
                        w-6 h-6
                        text-${operation.color}-600 dark:text-${operation.color}-400
                      `}
                    />
                  </div>
                  {operation.dangerous && (
                    <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400" />
                  )}
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  {operation.name}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {operation.description}
                </p>
                <div className="mt-3 text-xs font-mono text-gray-500 dark:text-gray-500 bg-gray-100 dark:bg-gray-900 p-2 rounded">
                  {operation.command}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Operation History */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Historial de Operaciones
        </h2>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            </div>
          ) : executions.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 text-gray-500 dark:text-gray-400">
              <Terminal className="w-12 h-12 mb-4" />
              <p>No hay operaciones ejecutadas</p>
            </div>
          ) : (
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Operación
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Estado
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Inicio
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Duración
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {executions.slice(0, 10).map((execution) => (
                  <tr
                    key={execution.id}
                    className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <Terminal className="w-5 h-5 text-gray-400 mr-3" />
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {execution.operation}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`
                          flex items-center gap-2 w-fit px-3 py-1 rounded-full text-xs font-medium
                          ${getStatusColor(execution.status)}
                        `}
                      >
                        {getStatusIcon(execution.status)}
                        {execution.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 dark:text-white">
                        {formatDate(execution.started_at)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 dark:text-white">
                        {calculateDuration(execution.started_at, execution.completed_at)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => handleViewOutput(execution)}
                        className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300 flex items-center gap-1 ml-auto"
                      >
                        <Terminal className="w-4 h-4" />
                        Ver Output
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Confirm Modal */}
      {showConfirmModal && selectedOperation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full">
            <div className="p-6">
              <div className="flex items-start gap-4">
                <div
                  className={`
                    p-3 rounded-full
                    ${
                      selectedOperation.dangerous
                        ? 'bg-red-100 dark:bg-red-900/30'
                        : 'bg-blue-100 dark:bg-blue-900/30'
                    }
                  `}
                >
                  {selectedOperation.dangerous ? (
                    <AlertTriangle className="w-6 h-6 text-red-600 dark:text-red-400" />
                  ) : (
                    <Play className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                  )}
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    Confirmar Operación
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    ¿Estás seguro de ejecutar <strong>{selectedOperation.name}</strong>?
                  </p>
                  <div className="bg-gray-50 dark:bg-gray-900 p-3 rounded-lg mb-4">
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                      {selectedOperation.description}
                    </p>
                    <code className="text-xs font-mono text-gray-800 dark:text-gray-300">
                      {selectedOperation.command}
                    </code>
                  </div>
                  {selectedOperation.dangerous && (
                    <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-3 rounded-lg mb-4">
                      <p className="text-sm text-red-600 dark:text-red-400">
                        ⚠️ Esta operación es peligrosa y puede causar tiempo de inactividad.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
            <div className="bg-gray-50 dark:bg-gray-700 px-6 py-4 flex justify-end gap-3 rounded-b-lg">
              <button
                onClick={() => {
                  setShowConfirmModal(false);
                  setSelectedOperation(null);
                }}
                className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600"
              >
                Cancelar
              </button>
              <button
                onClick={handleConfirmExecution}
                disabled={executeMutation.isPending}
                className={`
                  px-4 py-2 text-white rounded-lg flex items-center gap-2 disabled:opacity-50
                  ${
                    selectedOperation.dangerous
                      ? 'bg-red-600 hover:bg-red-700'
                      : 'bg-blue-600 hover:bg-blue-700'
                  }
                `}
              >
                {executeMutation.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
                Ejecutar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Output Modal */}
      {showOutputModal && selectedExecution && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Output: {selectedExecution.operation}
                </h2>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  {formatDate(selectedExecution.started_at)}
                </p>
              </div>
              <button
                onClick={() => {
                  setShowOutputModal(false);
                  setSelectedExecution(null);
                }}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
              <div className="bg-gray-900 text-gray-100 p-4 rounded-lg font-mono text-sm overflow-x-auto">
                <pre className="whitespace-pre-wrap">
                  {selectedExecution.output || 'Sin output disponible...'}
                  {selectedExecution.error && (
                    <div className="text-red-400 mt-4">
                      ERROR: {selectedExecution.error}
                    </div>
                  )}
                </pre>
              </div>
            </div>

            <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <span
                className={`
                  flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium
                  ${getStatusColor(selectedExecution.status)}
                `}
              >
                {getStatusIcon(selectedExecution.status)}
                {selectedExecution.status}
              </span>
              <button
                onClick={() => {
                  setShowOutputModal(false);
                  setSelectedExecution(null);
                }}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OperationsPanel;
