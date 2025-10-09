'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { cdmService } from '@/services/cdm';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/toast';
import { PlusIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/outline';
import { Entity, EntityCreate } from '@/types/api';

interface EntityFormProps {
  entity?: Entity;
  onSubmit: (data: EntityCreate) => void;
  onCancel: () => void;
  isLoading: boolean;
}

function EntityForm({ entity, onSubmit, onCancel, isLoading }: EntityFormProps) {
  const [formData, setFormData] = useState<EntityCreate>({
    company_name: entity?.company_name || '',
    financial_year_start: entity?.financial_year_start || '',
    financial_year_end: entity?.financial_year_end || '',
    currency: entity?.currency || 'INR',
    gstin: entity?.gstin || '',
    pan: entity?.pan || '',
    state: entity?.state || '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div className="mt-3">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            {entity ? 'Edit Company' : 'Add New Company'}
          </h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Company Name *</label>
              <input
                type="text"
                required
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                value={formData.company_name}
                onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">FY Start *</label>
                <input
                  type="date"
                  required
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  value={formData.financial_year_start}
                  onChange={(e) => setFormData({ ...formData, financial_year_start: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">FY End *</label>
                <input
                  type="date"
                  required
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  value={formData.financial_year_end}
                  onChange={(e) => setFormData({ ...formData, financial_year_end: e.target.value })}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">GSTIN</label>
              <input
                type="text"
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                value={formData.gstin}
                onChange={(e) => setFormData({ ...formData, gstin: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">PAN</label>
              <input
                type="text"
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                value={formData.pan}
                onChange={(e) => setFormData({ ...formData, pan: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">State</label>
              <input
                type="text"
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                value={formData.state}
                onChange={(e) => setFormData({ ...formData, state: e.target.value })}
              />
            </div>

            <div className="flex justify-end space-x-3 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? 'Saving...' : (entity ? 'Update' : 'Create')}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default function EntitiesPage() {
  const [showForm, setShowForm] = useState(false);
  const [editingEntity, setEditingEntity] = useState<Entity | null>(null);
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: entities, isLoading } = useQuery({
    queryKey: ['entities'],
    queryFn: () => cdmService.getEntities({ limit: 100 }),
  });

  const createMutation = useMutation({
    mutationFn: cdmService.createEntity,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['entities'] });
      setShowForm(false);
      toast('Company created successfully!', 'success');
    },
    onError: (error: any) => {
      toast(error?.response?.data?.detail || 'Failed to create company', 'error');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<EntityCreate> }) =>
      cdmService.updateEntity(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['entities'] });
      setEditingEntity(null);
      setShowForm(false);
      toast('Company updated successfully!', 'success');
    },
    onError: (error: any) => {
      toast(error?.response?.data?.detail || 'Failed to update company', 'error');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: cdmService.deleteEntity,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['entities'] });
      toast('Company deleted successfully!', 'success');
    },
    onError: (error: any) => {
      toast(error?.response?.data?.detail || 'Failed to delete company', 'error');
    },
  });

  const handleSubmit = (data: EntityCreate) => {
    if (editingEntity) {
      updateMutation.mutate({ id: editingEntity.company_id, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleEdit = (entity: Entity) => {
    setEditingEntity(entity);
    setShowForm(true);
  };

  const handleDelete = (entityId: string) => {
    if (confirm('Are you sure you want to delete this company?')) {
      deleteMutation.mutate(entityId);
    }
  };

  const handleCloseForm = () => {
    setShowForm(false);
    setEditingEntity(null);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Companies</h1>
        <Button
          onClick={() => setShowForm(true)}
          className="flex items-center space-x-2"
        >
          <PlusIcon className="h-4 w-4" />
          <span>Add Company</span>
        </Button>
      </div>

      <div className="bg-white shadow rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Company Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                GSTIN
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Financial Year
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                State
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {entities?.map((entity) => (
              <tr key={entity.company_id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{entity.company_name}</div>
                  <div className="text-sm text-gray-500">{entity.pan}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {entity.gstin || '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {new Date(entity.financial_year_start).getFullYear()} - {new Date(entity.financial_year_end).getFullYear()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {entity.state || '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                  <button
                    onClick={() => handleEdit(entity)}
                    className="text-blue-600 hover:text-blue-900"
                  >
                    <PencilIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(entity.company_id)}
                    className="text-red-600 hover:text-red-900"
                    disabled={deleteMutation.isPending}
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showForm && (
        <EntityForm
          entity={editingEntity || undefined}
          onSubmit={handleSubmit}
          onCancel={handleCloseForm}
          isLoading={createMutation.isPending || updateMutation.isPending}
        />
      )}
    </div>
  );
}