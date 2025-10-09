'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '@/store/auth';
import { cdmService } from '@/services/cdm';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/toast';
import { PlusIcon, PencilIcon, EyeIcon } from '@heroicons/react/24/outline';
import { VoucherHeader, VoucherCreate, VoucherStatus, ReconciliationStatus } from '@/types/api';

interface VoucherFormProps {
  voucher?: VoucherHeader;
  onSubmit: (data: VoucherCreate) => void;
  onCancel: () => void;
  isLoading: boolean;
}

function VoucherForm({ voucher, onSubmit, onCancel, isLoading }: VoucherFormProps) {
  const [formData, setFormData] = useState<VoucherCreate>({
    voucher_type: voucher?.voucher_type || 'Payment',
    voucher_date: voucher?.voucher_date || new Date().toISOString().split('T')[0],
    voucher_number: voucher?.voucher_number || '',
    narration: voucher?.narration || '',
    total_amount: voucher?.total_amount || 0,
    is_gst_applicable: voucher?.is_gst_applicable || false,
    lines: []
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
            {voucher ? 'Edit Voucher' : 'Add New Voucher'}
          </h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Voucher Type *</label>
                <select
                  required
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  value={formData.voucher_type}
                  onChange={(e) => setFormData({ ...formData, voucher_type: e.target.value })}
                >
                  <option value="Payment">Payment</option>
                  <option value="Receipt">Receipt</option>
                  <option value="Sales">Sales</option>
                  <option value="Purchase">Purchase</option>
                  <option value="Journal">Journal</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Voucher Number *</label>
                <input
                  type="text"
                  required
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  value={formData.voucher_number}
                  onChange={(e) => setFormData({ ...formData, voucher_number: e.target.value })}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Date *</label>
              <input
                type="date"
                required
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                value={formData.voucher_date}
                onChange={(e) => setFormData({ ...formData, voucher_date: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Amount *</label>
              <input
                type="number"
                step="0.01"
                required
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                value={formData.total_amount}
                onChange={(e) => setFormData({ ...formData, total_amount: parseFloat(e.target.value) })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Narration</label>
              <textarea
                rows={3}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                value={formData.narration}
                onChange={(e) => setFormData({ ...formData, narration: e.target.value })}
              />
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="gst_applicable"
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                checked={formData.is_gst_applicable}
                onChange={(e) => setFormData({ ...formData, is_gst_applicable: e.target.checked })}
              />
              <label htmlFor="gst_applicable" className="ml-2 block text-sm text-gray-900">
                GST Applicable
              </label>
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
                {isLoading ? 'Saving...' : (voucher ? 'Update' : 'Create')}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

function getStatusBadge(status: VoucherStatus) {
  const baseClasses = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium";
  switch (status) {
    case VoucherStatus.POSTED:
      return `${baseClasses} bg-green-100 text-green-800`;
    case VoucherStatus.VERIFIED:
      return `${baseClasses} bg-blue-100 text-blue-800`;
    case VoucherStatus.DRAFT:
      return `${baseClasses} bg-gray-100 text-gray-800`;
    default:
      return `${baseClasses} bg-gray-100 text-gray-800`;
  }
}

function getReconciliationBadge(status: ReconciliationStatus) {
  const baseClasses = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium";
  switch (status) {
    case ReconciliationStatus.AUTO_MATCHED:
      return `${baseClasses} bg-green-100 text-green-800`;
    case ReconciliationStatus.MANUALLY_VERIFIED:
      return `${baseClasses} bg-blue-100 text-blue-800`;
    case ReconciliationStatus.DISPUTED:
      return `${baseClasses} bg-red-100 text-red-800`;
    case ReconciliationStatus.UNMATCHED:
    default:
      return `${baseClasses} bg-yellow-100 text-yellow-800`;
  }
}

export default function VouchersPage() {
  const [showForm, setShowForm] = useState(false);
  const [editingVoucher, setEditingVoucher] = useState<VoucherHeader | null>(null);
  const [filters, setFilters] = useState({
    voucher_type: '',
    status: '',
    from_date: '',
    to_date: ''
  });
  
  const { selectedCompanyId } = useAuthStore();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: vouchers, isLoading } = useQuery({
    queryKey: ['vouchers', selectedCompanyId, filters],
    queryFn: () => selectedCompanyId ? cdmService.getVouchers({
      limit: 100,
      ...filters
    }) : null,
    enabled: !!selectedCompanyId,
  });

  const createMutation = useMutation({
    mutationFn: cdmService.createVoucher,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vouchers'] });
      setShowForm(false);
      toast('Voucher created successfully!', 'success');
    },
    onError: (error: any) => {
      toast(error?.response?.data?.detail || 'Failed to create voucher', 'error');
    },
  });

  const handleSubmit = (data: VoucherCreate) => {
    createMutation.mutate(data);
  };

  const handleEdit = (voucher: VoucherHeader) => {
    setEditingVoucher(voucher);
    setShowForm(true);
  };

  const handleCloseForm = () => {
    setShowForm(false);
    setEditingVoucher(null);
  };

  if (!selectedCompanyId) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
        <div className="flex">
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">
              No Company Selected
            </h3>
            <div className="mt-2 text-sm text-yellow-700">
              <p>Please select a company to view vouchers.</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

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
        <h1 className="text-2xl font-bold text-gray-900">Vouchers</h1>
        <Button
          onClick={() => setShowForm(true)}
          className="flex items-center space-x-2"
        >
          <PlusIcon className="h-4 w-4" />
          <span>Add Voucher</span>
        </Button>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Voucher Type</label>
            <select
              className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              value={filters.voucher_type}
              onChange={(e) => setFilters({ ...filters, voucher_type: e.target.value })}
            >
              <option value="">All Types</option>
              <option value="Payment">Payment</option>
              <option value="Receipt">Receipt</option>
              <option value="Sales">Sales</option>
              <option value="Purchase">Purchase</option>
              <option value="Journal">Journal</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Status</label>
            <select
              className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            >
              <option value="">All Statuses</option>
              <option value="Draft">Draft</option>
              <option value="Posted">Posted</option>
              <option value="Verified">Verified</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">From Date</label>
            <input
              type="date"
              className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              value={filters.from_date}
              onChange={(e) => setFilters({ ...filters, from_date: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">To Date</label>
            <input
              type="date"
              className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              value={filters.to_date}
              onChange={(e) => setFilters({ ...filters, to_date: e.target.value })}
            />
          </div>
        </div>
      </div>

      {/* Vouchers Table */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Voucher No.
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Amount
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Reconciliation
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {vouchers?.map((voucher) => (
              <tr key={voucher.voucher_id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{voucher.voucher_number}</div>
                  <div className="text-sm text-gray-500">{voucher.narration?.slice(0, 30)}...</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                    {voucher.voucher_type}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {new Date(voucher.voucher_date).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ₹{voucher.total_amount.toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={getStatusBadge(voucher.status)}>
                    {voucher.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={getReconciliationBadge(voucher.reconciliation_status)}>
                    {voucher.reconciliation_status.replace('_', ' ')}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                  <button
                    onClick={() => handleEdit(voucher)}
                    className="text-blue-600 hover:text-blue-900"
                  >
                    <EyeIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleEdit(voucher)}
                    className="text-green-600 hover:text-green-900"
                  >
                    <PencilIcon className="h-4 w-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {(!vouchers || vouchers.length === 0) && (
          <div className="text-center py-12">
            <div className="text-gray-500">
              <p>No vouchers found</p>
              <p className="text-sm mt-2">Create your first voucher to get started</p>
            </div>
          </div>
        )}
      </div>

      {showForm && (
        <VoucherForm
          voucher={editingVoucher || undefined}
          onSubmit={handleSubmit}
          onCancel={handleCloseForm}
          isLoading={createMutation.isPending}
        />
      )}
    </div>
  );
}