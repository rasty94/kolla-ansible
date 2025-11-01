import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { 
  CheckCircle2, 
  Circle, 
  Server, 
  Settings, 
  FileText, 
  Play,
  AlertCircle,
  Loader2
} from 'lucide-react';
import toast from 'react-hot-toast';

// Schema de validación para cada paso
const step1Schema = z.object({
  deploymentName: z.string().min(3, 'Mínimo 3 caracteres').max(50),
  environment: z.enum(['production', 'staging', 'development']),
  description: z.string().optional(),
});

const step2Schema = z.object({
  services: z.array(z.string()).min(1, 'Selecciona al menos un servicio'),
});

const step3Schema = z.object({
  networkInterface: z.string().min(1, 'Interfaz requerida'),
  networkCIDR: z.string().regex(/^(\d{1,3}\.){3}\d{1,3}\/\d{1,2}$/, 'CIDR inválido'),
  enableHA: z.boolean(),
  enableTLS: z.boolean(),
});

type Step1Data = z.infer<typeof step1Schema>;
type Step2Data = z.infer<typeof step2Schema>;
type Step3Data = z.infer<typeof step3Schema>;

interface DeploymentData extends Step1Data, Step2Data, Step3Data {}

const KOLLA_SERVICES = [
  { id: 'keystone', name: 'Keystone', category: 'Identity' },
  { id: 'glance', name: 'Glance', category: 'Image' },
  { id: 'nova', name: 'Nova', category: 'Compute' },
  { id: 'neutron', name: 'Neutron', category: 'Network' },
  { id: 'cinder', name: 'Cinder', category: 'Block Storage' },
  { id: 'horizon', name: 'Horizon', category: 'Dashboard' },
  { id: 'heat', name: 'Heat', category: 'Orchestration' },
  { id: 'swift', name: 'Swift', category: 'Object Storage' },
  { id: 'octavia', name: 'Octavia', category: 'Load Balancer' },
  { id: 'barbican', name: 'Barbican', category: 'Key Manager' },
  { id: 'designate', name: 'Designate', category: 'DNS' },
  { id: 'manila', name: 'Manila', category: 'Shared Filesystem' },
];

const DeploymentWizard: React.FC = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [deploymentData, setDeploymentData] = useState<Partial<DeploymentData>>({});

  // Form para Step 1
  const {
    register: registerStep1,
    handleSubmit: handleSubmitStep1,
    formState: { errors: errorsStep1 },
  } = useForm<Step1Data>({
    resolver: zodResolver(step1Schema),
    defaultValues: deploymentData as Step1Data,
  });

  // Form para Step 2
  const {
    register: registerStep2,
    handleSubmit: handleSubmitStep2,
    watch: watchStep2,
    formState: { errors: errorsStep2 },
  } = useForm<Step2Data>({
    resolver: zodResolver(step2Schema),
    defaultValues: { services: deploymentData.services || [] },
  });

  const selectedServices = watchStep2('services') || [];

  // Form para Step 3
  const {
    register: registerStep3,
    handleSubmit: handleSubmitStep3,
    formState: { errors: errorsStep3 },
  } = useForm<Step3Data>({
    resolver: zodResolver(step3Schema),
    defaultValues: {
      networkInterface: deploymentData.networkInterface || 'eth0',
      networkCIDR: deploymentData.networkCIDR || '10.0.0.0/24',
      enableHA: deploymentData.enableHA || false,
      enableTLS: deploymentData.enableTLS || false,
    },
  });

  // Mutation para crear deployment
  const createDeployment = useMutation({
    mutationFn: async (data: DeploymentData) => {
      const response = await fetch('/api/deployments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error('Error al crear deployment');
      return response.json();
    },
    onSuccess: () => {
      toast.success('Deployment creado exitosamente');
      navigate('/deployments');
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });

  const onStep1Submit = (data: Step1Data) => {
    setDeploymentData((prev) => ({ ...prev, ...data }));
    setCurrentStep(2);
  };

  const onStep2Submit = (data: Step2Data) => {
    setDeploymentData((prev) => ({ ...prev, ...data }));
    setCurrentStep(3);
  };

  const onStep3Submit = (data: Step3Data) => {
    const finalData = { ...deploymentData, ...data } as DeploymentData;
    setDeploymentData(finalData);
    setCurrentStep(4);
  };

  const onFinalSubmit = () => {
    createDeployment.mutate(deploymentData as DeploymentData);
  };

  const steps = [
    { number: 1, title: 'Información Básica', icon: FileText },
    { number: 2, title: 'Selección de Servicios', icon: Server },
    { number: 3, title: 'Configuración de Red', icon: Settings },
    { number: 4, title: 'Revisión', icon: CheckCircle2 },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Nuevo Deployment
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Configura tu deployment de OpenStack paso a paso
          </p>
        </div>

        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => {
              const Icon = step.icon;
              const isCompleted = currentStep > step.number;
              const isCurrent = currentStep === step.number;

              return (
                <React.Fragment key={step.number}>
                  <div className="flex flex-col items-center">
                    <div
                      className={`
                        w-12 h-12 rounded-full flex items-center justify-center border-2
                        ${
                          isCompleted
                            ? 'bg-green-500 border-green-500 text-white'
                            : isCurrent
                            ? 'bg-blue-500 border-blue-500 text-white'
                            : 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-400'
                        }
                      `}
                    >
                      {isCompleted ? <CheckCircle2 className="w-6 h-6" /> : <Icon className="w-6 h-6" />}
                    </div>
                    <span
                      className={`
                        mt-2 text-sm font-medium
                        ${isCurrent ? 'text-blue-600 dark:text-blue-400' : 'text-gray-500 dark:text-gray-400'}
                      `}
                    >
                      {step.title}
                    </span>
                  </div>
                  {index < steps.length - 1 && (
                    <div
                      className={`
                        flex-1 h-0.5 mx-4
                        ${isCompleted ? 'bg-green-500' : 'bg-gray-300 dark:bg-gray-600'}
                      `}
                    />
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>

        {/* Content Card */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
          {/* Step 1: Información Básica */}
          {currentStep === 1 && (
            <form onSubmit={handleSubmitStep1(onStep1Submit)} className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                Información Básica
              </h2>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Nombre del Deployment *
                </label>
                <input
                  {...registerStep1('deploymentName')}
                  type="text"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                  placeholder="my-openstack-cluster"
                />
                {errorsStep1.deploymentName && (
                  <p className="mt-1 text-sm text-red-600">{errorsStep1.deploymentName.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Entorno *
                </label>
                <select
                  {...registerStep1('environment')}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                >
                  <option value="production">Producción</option>
                  <option value="staging">Staging</option>
                  <option value="development">Desarrollo</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Descripción
                </label>
                <textarea
                  {...registerStep1('description')}
                  rows={4}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                  placeholder="Describe tu deployment..."
                />
              </div>

              <div className="flex justify-end">
                <button
                  type="submit"
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-4 focus:ring-blue-300"
                >
                  Siguiente
                </button>
              </div>
            </form>
          )}

          {/* Step 2: Selección de Servicios */}
          {currentStep === 2 && (
            <form onSubmit={handleSubmitStep2(onStep2Submit)} className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                Selección de Servicios
              </h2>

              <div className="grid grid-cols-2 gap-4">
                {KOLLA_SERVICES.map((service) => (
                  <label
                    key={service.id}
                    className="flex items-start p-4 border border-gray-300 dark:border-gray-600 rounded-lg cursor-pointer hover:border-blue-500 dark:hover:border-blue-400 transition-colors"
                  >
                    <input
                      type="checkbox"
                      value={service.id}
                      {...registerStep2('services')}
                      className="mt-1 w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                    />
                    <div className="ml-3">
                      <div className="font-medium text-gray-900 dark:text-white">
                        {service.name}
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {service.category}
                      </div>
                    </div>
                  </label>
                ))}
              </div>

              {errorsStep2.services && (
                <div className="flex items-center gap-2 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                  <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400" />
                  <p className="text-sm text-red-600 dark:text-red-400">
                    {errorsStep2.services.message}
                  </p>
                </div>
              )}

              <div className="flex justify-between">
                <button
                  type="button"
                  onClick={() => setCurrentStep(1)}
                  className="px-6 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  Anterior
                </button>
                <button
                  type="submit"
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-4 focus:ring-blue-300"
                >
                  Siguiente
                </button>
              </div>
            </form>
          )}

          {/* Step 3: Configuración de Red */}
          {currentStep === 3 && (
            <form onSubmit={handleSubmitStep3(onStep3Submit)} className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                Configuración de Red
              </h2>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Interfaz de Red *
                </label>
                <input
                  {...registerStep3('networkInterface')}
                  type="text"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                  placeholder="eth0"
                />
                {errorsStep3.networkInterface && (
                  <p className="mt-1 text-sm text-red-600">{errorsStep3.networkInterface.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Red CIDR *
                </label>
                <input
                  {...registerStep3('networkCIDR')}
                  type="text"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                  placeholder="10.0.0.0/24"
                />
                {errorsStep3.networkCIDR && (
                  <p className="mt-1 text-sm text-red-600">{errorsStep3.networkCIDR.message}</p>
                )}
              </div>

              <div className="space-y-4">
                <label className="flex items-center">
                  <input
                    {...registerStep3('enableHA')}
                    type="checkbox"
                    className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                  />
                  <span className="ml-3 text-sm font-medium text-gray-700 dark:text-gray-300">
                    Habilitar Alta Disponibilidad (HA)
                  </span>
                </label>

                <label className="flex items-center">
                  <input
                    {...registerStep3('enableTLS')}
                    type="checkbox"
                    className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                  />
                  <span className="ml-3 text-sm font-medium text-gray-700 dark:text-gray-300">
                    Habilitar TLS/SSL
                  </span>
                </label>
              </div>

              <div className="flex justify-between">
                <button
                  type="button"
                  onClick={() => setCurrentStep(2)}
                  className="px-6 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  Anterior
                </button>
                <button
                  type="submit"
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-4 focus:ring-blue-300"
                >
                  Revisar
                </button>
              </div>
            </form>
          )}

          {/* Step 4: Revisión */}
          {currentStep === 4 && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                Revisión Final
              </h2>

              <div className="space-y-4">
                <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                    Información Básica
                  </h3>
                  <dl className="grid grid-cols-2 gap-2 text-sm">
                    <dt className="text-gray-600 dark:text-gray-400">Nombre:</dt>
                    <dd className="text-gray-900 dark:text-white font-medium">
                      {deploymentData.deploymentName}
                    </dd>
                    <dt className="text-gray-600 dark:text-gray-400">Entorno:</dt>
                    <dd className="text-gray-900 dark:text-white font-medium">
                      {deploymentData.environment}
                    </dd>
                  </dl>
                </div>

                <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                    Servicios ({deploymentData.services?.length})
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {deploymentData.services?.map((serviceId) => {
                      const service = KOLLA_SERVICES.find((s) => s.id === serviceId);
                      return (
                        <span
                          key={serviceId}
                          className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 rounded-full text-sm"
                        >
                          {service?.name}
                        </span>
                      );
                    })}
                  </div>
                </div>

                <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                    Configuración de Red
                  </h3>
                  <dl className="grid grid-cols-2 gap-2 text-sm">
                    <dt className="text-gray-600 dark:text-gray-400">Interfaz:</dt>
                    <dd className="text-gray-900 dark:text-white font-medium">
                      {deploymentData.networkInterface}
                    </dd>
                    <dt className="text-gray-600 dark:text-gray-400">CIDR:</dt>
                    <dd className="text-gray-900 dark:text-white font-medium">
                      {deploymentData.networkCIDR}
                    </dd>
                    <dt className="text-gray-600 dark:text-gray-400">HA:</dt>
                    <dd className="text-gray-900 dark:text-white font-medium">
                      {deploymentData.enableHA ? 'Sí' : 'No'}
                    </dd>
                    <dt className="text-gray-600 dark:text-gray-400">TLS:</dt>
                    <dd className="text-gray-900 dark:text-white font-medium">
                      {deploymentData.enableTLS ? 'Sí' : 'No'}
                    </dd>
                  </dl>
                </div>
              </div>

              <div className="flex justify-between">
                <button
                  type="button"
                  onClick={() => setCurrentStep(3)}
                  className="px-6 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
                  disabled={createDeployment.isPending}
                >
                  Anterior
                </button>
                <button
                  onClick={onFinalSubmit}
                  disabled={createDeployment.isPending}
                  className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:ring-4 focus:ring-green-300 flex items-center gap-2 disabled:opacity-50"
                >
                  {createDeployment.isPending ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Creando...
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5" />
                      Crear Deployment
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DeploymentWizard;
