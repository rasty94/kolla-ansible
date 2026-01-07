import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Plus,
  Pencil,
  Trash2,
  Search,
  Server,
  CheckCircle,
  XCircle,
  Loader2,
  Download,
  X,
} from 'lucide-react';
import toast from 'react-hot-toast';

// Schema de validación para Host
const hostSchema = z.object({
  hostname: z.string().min(1, 'Hostname requerido'),
  ip_address: z.string().ip('IP inválida'),
  ssh_user: z.string().min(1, 'Usuario SSH requerido'),
  ssh_port: z.number().int().min(1).max(65535),
  roles: z.array(z.string()).min(1, 'Selecciona al menos un rol'),
  is_active: z.boolean(),
});

type Host = z.infer<typeof hostSchema> & { id: number };

const AVAILABLE_ROLES = [
  { id: 'control', name: 'Control', color: 'blue' },
  { id: 'compute', name: 'Compute', color: 'green' },
  { id: 'network', name: 'Network', color: 'purple' },
  { id: 'storage', name: 'Storage', color: 'orange' },
  { id: 'monitoring', name: 'Monitoring', color: 'pink' },
];

const InventoryManager: React.FC = () => {
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingHost, setEditingHost] = useState<Host | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRoleFilter, setSelectedRoleFilter] = useState<string>('all');

  // Fetch hosts
  const { data: hosts = [], isLoading } = useQuery<Host[]>({
    queryKey: ['hosts'],
    queryFn: async () => {
      const response = await fetch('/api/inventory/hosts');
      if (!response.ok) throw new Error('Error al cargar hosts');
      return response.json();
    },
  });

  // Form
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<Omit<Host, 'id'>>({
    resolver: zodResolver(hostSchema),
    defaultValues: editingHost || {
      hostname: '',
      ip_address: '',
      ssh_user: 'root',
      ssh_port: 22,
      roles: [],
      is_active: true,
    },
  });

  // Create mutation
  const createMutation = useMutation({
    mutationFn: async (data: Omit<Host, 'id'>) => {
      const response = await fetch('/api/inventory/hosts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error('Error al crear host');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['hosts'] });
      toast.success('Host creado exitosamente');
      setIsModalOpen(false);
      reset();
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: async (data: Host) => {
      const response = await fetch(`/api/inventory/hosts/${data.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error('Error al actualizar host');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['hosts'] });
      toast.success('Host actualizado exitosamente');
      setIsModalOpen(false);
      setEditingHost(null);
      reset();
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      const response = await fetch(`/api/inventory/hosts/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Error al eliminar host');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['hosts'] });
      toast.success('Host eliminado exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  // Generate Inventory Mutation
  const generateMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch('/api/inventory/generate', {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Error al generar inventario');
      return response.json();
    },
    onSuccess: () => {
      toast.success('Archivo de inventario generado exitosamente');
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  // Load Inventory Mutation
  const loadMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch('/api/inventory/load', {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Error al cargar inventario');
      return response.json();
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['hosts'] });
      toast.success(data.message);
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  const onSubmit = (data: Omit<Host, 'id'>) => {
    if (editingHost) {
      updateMutation.mutate({ ...data, id: editingHost.id });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleEdit = (host: Host) => {
    setEditingHost(host);
    reset(host);
    setIsModalOpen(true);
  };

  const handleDelete = (id: number) => {
    if (confirm('¿Estás seguro de eliminar este host?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleExport = () => {
    const dataStr = JSON.stringify(hosts, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'inventory.json';
    link.click();
    toast.success('Inventario exportado');
  };

  // Filtrar hosts
  const filteredHosts = hosts.filter((host) => {
    const matchesSearch =
      host.hostname.toLowerCase().includes(searchQuery.toLowerCase()) ||
      host.ip_address.includes(searchQuery);
    const matchesRole =
      selectedRoleFilter === 'all' || host.roles.includes(selectedRoleFilter);
    return matchesSearch && matchesRole;
  });

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Inventory Manager
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Gestiona los hosts de tu infraestructura OpenStack
        </p>
      </div>

      {/* Toolbar */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="flex gap-2 flex-1 w-full sm:w-auto">
          {/* Search */}
          <div className="relative flex-1 sm:w-80">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar hosts..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Role Filter */}
          <select
            value={selectedRoleFilter}
            onChange={(e) => setSelectedRoleFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Todos los roles</option>
            {AVAILABLE_ROLES.map((role) => (
              <option key={role.id} value={role.id}>
                {role.name}
              </option>
            ))}
          </select>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <button
            onClick={handleExport}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center gap-2"
          >
            <Download className="w-5 h-5" />
            Exportar
          </button>
          <button
            onClick={() => generateMutation.mutate()}
            disabled={generateMutation.isPending}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center gap-2"
          >
            {generateMutation.isPending ? <Loader2 className="w-5 h-5 animate-spin" /> : <Server className="w-5 h-5" />}
            Generar
          </button>
          <button
            onClick={() => loadMutation.mutate()}
            disabled={loadMutation.isPending}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center gap-2"
          >
            {loadMutation.isPending ? <Loader2 className="w-5 h-5 animate-spin" /> : <Download className="w-5 h-5" />}
            Cargar
          </button>
          <button
            onClick={() => {
              setEditingHost(null);
              reset();
              setIsModalOpen(true);
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Añadir Host
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
          <div className="text-sm text-gray-600 dark:text-gray-400">Total Hosts</div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {hosts.length}
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
          <div className="text-sm text-gray-600 dark:text-gray-400">Activos</div>
          <div className="text-2xl font-bold text-green-600">
            {hosts.filter((h) => h.is_active).length}
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
          <div className="text-sm text-gray-600 dark:text-gray-400">Compute Nodes</div>
          <div className="text-2xl font-bold text-blue-600">
            {hosts.filter((h) => h.roles.includes('compute')).length}
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
          <div className="text-sm text-gray-600 dark:text-gray-400">Control Nodes</div>
          <div className="text-2xl font-bold text-purple-600">
            {hosts.filter((h) => h.roles.includes('control')).length}
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        ) : filteredHosts.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-gray-500 dark:text-gray-400">
            <Server className="w-12 h-12 mb-4" />
            <p>No hay hosts disponibles</p>
          </div>
        ) : (
          <>
            {/* Desktop Table */}
            <table className="hidden md:table w-full">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Hostname
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    IP Address
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    SSH User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Roles
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Estado
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {filteredHosts.map((host) => (
                  <tr
                    key={host.id}
                    className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <Server className="w-5 h-5 text-gray-400 mr-3" />
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {host.hostname}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 dark:text-white">
                        {host.ip_address}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 dark:text-white">
                        {host.ssh_user}:{host.ssh_port}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-wrap gap-1">
                        {host.roles.map((roleId) => {
                          const role = AVAILABLE_ROLES.find((r) => r.id === roleId);
                          return (
                            <span
                              key={roleId}
                              className={`px-2 py-1 text-xs rounded-full bg-${role?.color}-100 dark:bg-${role?.color}-900/30 text-${role?.color}-800 dark:text-${role?.color}-300`}
                            >
                              {role?.name}
                            </span>
                          );
                        })}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {host.is_active ? (
                        <span className="flex items-center gap-1 text-green-600">
                          <CheckCircle className="w-4 h-4" />
                          <span className="text-sm">Activo</span>
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-red-600">
                          <XCircle className="w-4 h-4" />
                          <span className="text-sm">Inactivo</span>
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => handleEdit(host)}
                          className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300"
                        >
                          <Pencil className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => handleDelete(host.id)}
                          className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Mobile Cards */}
            <div className="md:hidden divide-y divide-gray-200 dark:divide-gray-700">
              {filteredHosts.map((host) => (
                <div key={host.id} className="p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Server className="w-5 h-5 text-gray-400" />
                      <div>
                        <h3 className="text-sm font-medium text-gray-900 dark:text-white">
                          {host.hostname}
                        </h3>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {host.ip_address}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleEdit(host)}
                        className="p-2 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-full"
                      >
                        <Pencil className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(host.id)}
                        className="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-full"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500 dark:text-gray-400">
                      {host.ssh_user}:{host.ssh_port}
                    </span>
                    {host.is_active ? (
                      <span className="flex items-center gap-1 text-green-600 text-xs">
                        <CheckCircle className="w-3 h-3" />
                        Activo
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-red-600 text-xs">
                        <XCircle className="w-3 h-3" />
                        Inactivo
                      </span>
                    )}
                  </div>

                  <div className="flex flex-wrap gap-1">
                    {host.roles.map((roleId) => {
                      const role = AVAILABLE_ROLES.find((r) => r.id === roleId);
                      return (
                        <span
                          key={roleId}
                          className={`px-2 py-1 text-xs rounded-full bg-${role?.color}-100 dark:bg-${role?.color}-900/30 text-${role?.color}-800 dark:text-${role?.color}-300`}
                        >
                          {role?.name}
                        </span>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6 flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                {editingHost ? 'Editar Host' : 'Nuevo Host'}
              </h2>
              <button
                onClick={() => {
                  setIsModalOpen(false);
                  setEditingHost(null);
                  reset();
                }}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Hostname *
                  </label>
                  <input
                    {...register('hostname')}
                    type="text"
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                    placeholder="controller-01"
                  />
                  {errors.hostname && (
                    <p className="mt-1 text-sm text-red-600">{errors.hostname.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    IP Address *
                  </label>
                  <input
                    {...register('ip_address')}
                    type="text"
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                    placeholder="192.168.1.10"
                  />
                  {errors.ip_address && (
                    <p className="mt-1 text-sm text-red-600">{errors.ip_address.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    SSH User *
                  </label>
                  <input
                    {...register('ssh_user')}
                    type="text"
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                    placeholder="root"
                  />
                  {errors.ssh_user && (
                    <p className="mt-1 text-sm text-red-600">{errors.ssh_user.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    SSH Port *
                  </label>
                  <input
                    {...register('ssh_port', { valueAsNumber: true })}
                    type="number"
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                    placeholder="22"
                  />
                  {errors.ssh_port && (
                    <p className="mt-1 text-sm text-red-600">{errors.ssh_port.message}</p>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Roles *
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {AVAILABLE_ROLES.map((role) => (
                    <label
                      key={role.id}
                      className="flex items-center p-3 border border-gray-300 dark:border-gray-600 rounded-lg cursor-pointer hover:border-blue-500 dark:hover:border-blue-400"
                    >
                      <input
                        type="checkbox"
                        value={role.id}
                        {...register('roles')}
                        className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                      />
                      <span className="ml-3 text-sm text-gray-900 dark:text-white">
                        {role.name}
                      </span>
                    </label>
                  ))}
                </div>
                {errors.roles && (
                  <p className="mt-1 text-sm text-red-600">{errors.roles.message}</p>
                )}
              </div>

              <div>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    {...register('is_active')}
                    className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                  />
                  <span className="ml-3 text-sm font-medium text-gray-700 dark:text-gray-300">
                    Host Activo
                  </span>
                </label>
              </div>

              <div className="flex justify-end gap-3 pt-6 border-t border-gray-200 dark:border-gray-700">
                <button
                  type="button"
                  onClick={() => {
                    setIsModalOpen(false);
                    setEditingHost(null);
                    reset();
                  }}
                  className="px-6 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={createMutation.isPending || updateMutation.isPending}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 flex items-center gap-2 disabled:opacity-50"
                >
                  {(createMutation.isPending || updateMutation.isPending) && (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  )}
                  {editingHost ? 'Actualizar' : 'Crear'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default InventoryManager;
