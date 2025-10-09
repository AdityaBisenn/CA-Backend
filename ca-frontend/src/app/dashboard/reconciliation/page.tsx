'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '@/store/auth';
import { cdmService } from '@/services/cdm';
import { 
  CheckCircleIcon, 
  ExclamationCircleIcon, 
  XCircleIcon,
  ArrowPathIcon 
} from '@heroicons/react/24/outline';

interface ReconciliationTabProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

function ReconciliationTabs({ activeTab, onTabChange }: ReconciliationTabProps) {
  const tabs = [
    { id: 'bank', label: 'Bank Statements', icon: '🏦' },
    { id: 'gst-sales', label: 'GST Sales', icon: '📊' },
    { id: 'gst-purchases', label: 'GST Purchases', icon: '📋' },
  ];

  return (
    <div className="border-b border-gray-200">
      <nav className="-mb-px flex space-x-8">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => onTabChange(tab.id)}
          >
            <span className="mr-2">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </nav>
    </div>
  );
}

function getStatusIcon(status: string) {
  switch (status) {
    case 'Matched':
      return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
    case 'Near_Match':
      return <ExclamationCircleIcon className="h-5 w-5 text-yellow-500" />;
    case 'Unmatched':
      return <XCircleIcon className="h-5 w-5 text-red-500" />;
    default:
      return <XCircleIcon className="h-5 w-5 text-gray-500" />;
  }
}

function getStatusBadge(status: string) {
  const baseClasses = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium";
  switch (status) {
    case 'Matched':
      return `${baseClasses} bg-green-100 text-green-800`;
    case 'Near_Match':
      return `${baseClasses} bg-yellow-100 text-yellow-800`;
    case 'Unmatched':
      return `${baseClasses} bg-red-100 text-red-800`;
    default:
      return `${baseClasses} bg-gray-100 text-gray-800`;
  }
}

export default function ReconciliationPage() {
  const [activeTab, setActiveTab] = useState('bank');
  const { selectedCompanyId } = useAuthStore();

  const { data: bankStatements, isLoading: loadingBank } = useQuery({
    queryKey: ['bank-statements', selectedCompanyId],
    queryFn: () => selectedCompanyId ? cdmService.getBankStatements({ limit: 100 }) : null,
    enabled: !!selectedCompanyId && activeTab === 'bank',
  });

  const { data: gstSales, isLoading: loadingGstSales } = useQuery({
    queryKey: ['gst-sales', selectedCompanyId],
    queryFn: () => selectedCompanyId ? cdmService.getGSTSales({ limit: 100 }) : null,
    enabled: !!selectedCompanyId && activeTab === 'gst-sales',
  });

  const { data: gstPurchases, isLoading: loadingGstPurchases } = useQuery({
    queryKey: ['gst-purchases', selectedCompanyId],
    queryFn: () => selectedCompanyId ? cdmService.getGSTPurchases({ limit: 100 }) : null,
    enabled: !!selectedCompanyId && activeTab === 'gst-purchases',
  });

  if (!selectedCompanyId) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
        <div className="flex">
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">
              No Company Selected
            </h3>
            <div className="mt-2 text-sm text-yellow-700">
              <p>Please select a company to view reconciliation data.</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const isLoading = loadingBank || loadingGstSales || loadingGstPurchases;

  // Calculate reconciliation stats
  const calculateStats = (data: any[]) => {
    if (!data) return { matched: 0, nearMatch: 0, unmatched: 0, total: 0 };
    const matched = data.filter(item => item.reconciliation_status === 'Matched').length;
    const nearMatch = data.filter(item => item.reconciliation_status === 'Near_Match').length;
    const unmatched = data.filter(item => item.reconciliation_status === 'Unmatched').length;
    return { matched, nearMatch, unmatched, total: data.length };
  };

  const getCurrentData = () => {
    switch (activeTab) {
      case 'bank':
        return bankStatements || [];
      case 'gst-sales':
        return gstSales || [];
      case 'gst-purchases':
        return gstPurchases || [];
      default:
        return [];
    }
  };

  const currentData = getCurrentData();
  const stats = calculateStats(currentData);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Reconciliation</h1>
        <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
          <ArrowPathIcon className="h-4 w-4" />
          <span>Run Reconciliation</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <CheckCircleIcon className="h-8 w-8 text-green-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Matched</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.matched}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <ExclamationCircleIcon className="h-8 w-8 text-yellow-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Near Match</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.nearMatch}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <XCircleIcon className="h-8 w-8 text-red-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Unmatched</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.unmatched}</p>
            </div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="h-8 w-8 bg-blue-500 rounded-full flex items-center justify-center">
              <span className="text-white font-semibold">%</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Match Rate</p>
              <p className="text-2xl font-semibold text-gray-900">
                {stats.total > 0 ? Math.round((stats.matched / stats.total) * 100) : 0}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Reconciliation Data */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4">
          <ReconciliationTabs activeTab={activeTab} onTabChange={setActiveTab} />
        </div>

        <div className="overflow-x-auto">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {activeTab === 'bank' ? 'Transaction' : 'Invoice'}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Description
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {currentData.map((item: any, index) => (
                  <tr key={item.bank_txn_id || item.gst_invoice_id || item.purchase_id || index}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {getStatusIcon(item.reconciliation_status)}
                        <span className={`ml-2 ${getStatusBadge(item.reconciliation_status)}`}>
                          {item.reconciliation_status.replace('_', ' ')}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {item.cheque_ref || item.invoice_number || '-'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(item.txn_date || item.invoice_date).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      ₹{(item.amount || item.total_value || 0).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {item.narration || item.gstin_customer || item.supplier_gstin || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}