import React, { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Save, Download, RotateCcw, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

interface ConfigFile {
  id: string;
  name: string;
  path: string;
  content: string;
  lastModified: string;
  size: number;
}

const AVAILABLE_CONFIGS = [
  {
    id: 'globals',
    name: 'globals.yml',
    path: '/etc/kolla/globals.yml',
    description: 'Configuración global de Kolla'
  },
  {
    id: 'passwords',
    name: 'passwords.yml',
    path: '/etc/kolla/passwords.yml',
    description: 'Contraseñas de servicios'
  },
  {
    id: 'inventory',
    name: 'inventory.ini',
    path: '/etc/kolla/inventory.ini',
    description: 'Inventario de hosts Ansible'
  },
  {
    id: 'multinode',
    name: 'multinode',
    path: '/etc/kolla/config/multinode',
    description: 'Configuración multinodo'
  }
];

export const ConfigEditor: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedConfig, setSelectedConfig] = useState<string>('globals');
  const [editorContent, setEditorContent] = useState<string>('');
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [isValidYaml, setIsValidYaml] = useState(true);

  // Fetch config file content
  const { data: configFile, isLoading, error } = useQuery<ConfigFile>({
    queryKey: ['config', selectedConfig],
    queryFn: async () => {
      const response = await fetch(`/api/config/${selectedConfig}`);
      if (!response.ok) {
        // Return mock data for demo
        const config = AVAILABLE_CONFIGS.find(c => c.id === selectedConfig);
        return {
          id: selectedConfig,
          name: config?.name || 'unknown.yml',
          path: config?.path || '/etc/kolla/config.yml',
          content: `# ${config?.name || 'Configuration file'}
# This is a mock configuration for demonstration
# In a real implementation, this would be loaded from the backend

global:
  kolla_base_distro: "ubuntu"
  kolla_install_type: "source"
  openstack_release: "2025.1"
  kolla_internal_vip_address: "10.0.0.10"
  kolla_external_vip_address: "192.168.1.10"
  network_interface: "eth0"
  neutron_external_interface: "eth1"

keystone:
  admin_password: "CHANGEME"

nova:
  libvirt_type: "kvm"

neutron:
  plugin: "ml2"
  type_drivers: "flat,vlan,vxlan"
  mechanism_drivers: "openvswitch,l2population"

cinder:
  volume_driver: "cinder.volume.drivers.lvm.LVMVolumeDriver"
  volume_group: "cinder-volumes"

glance:
  default_store: "file"

horizon:
  listen_port: "80"
`,
          lastModified: new Date().toISOString(),
          size: 1024
        };
      }
      return response.json();
    }
  });

  // Update editor content when configFile changes
  useEffect(() => {
    if (configFile) {
      setEditorContent(configFile.content);
      setHasUnsavedChanges(false);
    }
  }, [configFile]);

  // Save config mutation
  const saveMutation = useMutation({
    mutationFn: async (data: { id: string; content: string }) => {
      const response = await fetch(`/api/config/${data.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: data.content }),
      });
      if (!response.ok) throw new Error('Error al guardar configuración');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['config', selectedConfig] });
      setHasUnsavedChanges(false);
      toast.success('Configuración guardada exitosamente');
    },
    onError: (error: Error) => {
      toast.error(`Error al guardar: ${error.message}`);
    },
  });

  // Validate YAML
  const validateYaml = (content: string) => {
    try {
      // Basic YAML validation - in a real app, use a proper YAML parser
      if (content.trim() === '') {
        setIsValidYaml(false);
        return;
      }
      // Simple check for common YAML issues
      const lines = content.split('\n');
      let indentLevel = 0;
      for (const line of lines) {
        if (line.trim().startsWith('#')) continue; // Skip comments
        if (line.trim() === '') continue; // Skip empty lines

        const indent = line.length - line.trimStart().length;
        if (indent > indentLevel + 2) {
          setIsValidYaml(false);
          return;
        }
        indentLevel = indent;
      }
      setIsValidYaml(true);
    } catch (error) {
      setIsValidYaml(false);
    }
  };

  useEffect(() => {
    if (editorContent) {
      validateYaml(editorContent);
    }
  }, [editorContent]);

  const handleEditorChange = (value: string | undefined) => {
    const newContent = value || '';
    setEditorContent(newContent);
    setHasUnsavedChanges(true);
  };

  const handleSave = () => {
    if (!isValidYaml) {
      toast.error('No se puede guardar: YAML inválido');
      return;
    }
    saveMutation.mutate({ id: selectedConfig, content: editorContent });
  };

  const handleDownload = () => {
    const blob = new Blob([editorContent], { type: 'text/yaml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${selectedConfig}.yml`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('Archivo descargado');
  };

  const handleReset = () => {
    if (configFile && configFile.content) {
      setEditorContent(configFile.content);
      setHasUnsavedChanges(false);
      toast.success('Cambios descartados');
    }
  };

  const selectedConfigInfo = AVAILABLE_CONFIGS.find(c => c.id === selectedConfig);

  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div className="flex items-center space-x-4">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Config Editor</h1>
          <div className="flex items-center space-x-2">
            <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm ${
              isValidYaml ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
            }`}>
              {isValidYaml ? <CheckCircle className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
              <span>{isValidYaml ? 'YAML válido' : 'YAML inválido'}</span>
            </div>
            {hasUnsavedChanges && (
              <div className="flex items-center space-x-2 px-3 py-1 rounded-full text-sm bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300">
                <AlertCircle className="w-4 h-4" />
                <span>Cambios sin guardar</span>
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleReset}
            disabled={!hasUnsavedChanges}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <RotateCcw className="w-4 h-4" />
            Reset
          </button>

          <button
            onClick={handleDownload}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            Download
          </button>

          <button
            onClick={handleSave}
            disabled={!hasUnsavedChanges || !isValidYaml || saveMutation.isPending}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {saveMutation.isPending ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Save className="w-4 h-4" />
            )}
            Save
          </button>
        </div>
      </div>

      {/* Config Selector */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div className="flex items-center space-x-4">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Archivo de configuración:
          </label>
          <select
            value={selectedConfig}
            onChange={(e) => setSelectedConfig(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
          >
            {AVAILABLE_CONFIGS.map((config) => (
              <option key={config.id} value={config.id}>
                {config.name} - {config.description}
              </option>
            ))}
          </select>
          {selectedConfigInfo && (
            <div className="text-sm text-gray-500 dark:text-gray-400">
              📁 {selectedConfigInfo.path}
            </div>
          )}
        </div>
      </div>

      {/* Editor */}
      <div className="flex-1 p-4">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-400">Cargando configuración...</p>
            </div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <AlertCircle className="w-12 h-12 text-red-600 mx-auto mb-4" />
              <p className="text-gray-900 dark:text-white font-medium">Error al cargar configuración</p>
              <p className="text-gray-600 dark:text-gray-400 text-sm mt-2">
                Usando configuración de ejemplo para demostración
              </p>
            </div>
          </div>
        ) : (
          <div className="h-full border border-gray-300 dark:border-gray-600 rounded-lg overflow-hidden">
            <Editor
              height="100%"
              language="yaml"
              value={editorContent}
              onChange={handleEditorChange}
              theme="vs-dark"
              options={{
                minimap: { enabled: true },
                fontSize: 14,
                lineNumbers: 'on',
                renderWhitespace: 'selection',
                automaticLayout: true,
                wordWrap: 'on',
                scrollBeyondLastLine: false,
                tabSize: 2,
                insertSpaces: true,
                folding: true,
                autoClosingBrackets: 'always',
                autoClosingQuotes: 'always',
                suggestOnTriggerCharacters: true,
                quickSuggestions: {
                  other: true,
                  comments: false,
                  strings: true
                }
              }}
              loading={
                <div className="flex items-center justify-center h-full">
                  <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
                </div>
              }
            />
          </div>
        )}
      </div>

      {/* Status Bar */}
      <div className="px-4 py-2 bg-gray-100 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 text-xs text-gray-600 dark:text-gray-400 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <span>Archivo: {selectedConfigInfo?.name}</span>
          <span>Ruta: {selectedConfigInfo?.path}</span>
          {configFile ? (
            <>
              <span>Tamaño: {(configFile.size / 1024).toFixed(1)} KB</span>
              <span>Modificado: {new Date(configFile.lastModified).toLocaleString()}</span>
            </>
          ) : null}
        </div>
        <div className="flex items-center space-x-4">
          <span>Modo: YAML</span>
          <span>Tema: Dark</span>
          <span>Estado: {saveMutation.isPending ? 'Guardando...' : hasUnsavedChanges ? 'Modificado' : 'Guardado'}</span>
        </div>
      </div>
    </div>
  );
};