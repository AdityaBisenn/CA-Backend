'use client';

import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '@/store/auth';
import { cdmService } from '@/services/cdm';
import { 
  BuildingOfficeIcon,
  DocumentTextIcon,
  BanknotesIcon,
  ChartBarIcon 
} from '@heroicons/react/24/outline';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ComponentType<any>;
  color: string;
  change?: string;
}

function StatCard({ title, value, icon: Icon, color, change }: StatCardProps) {
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex items-center">
        <div className={`p-2 rounded-lg ${color}`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
        <div className="ml-4">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-semibold text-gray-900">{value}</p>
          {change && (
            <p className="text-sm text-green-600">{change}</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { selectedCompanyId } = useAuthStore();

  const { data: entities } = useQuery({
    queryKey: ['entities'],
    queryFn: () => cdmService.getEntities({ limit: 100 }),
  });

  const { data: vouchers } = useQuery({
    queryKey: ['vouchers', selectedCompanyId],
    queryFn: () => selectedCompanyId ? cdmService.getVouchers({ limit: 100 }) : null,
    enabled: !!selectedCompanyId,
  });

  const { data: bankStatements } = useQuery({
    queryKey: ['bank-statements', selectedCompanyId],
    queryFn: () => selectedCompanyId ? cdmService.getBankStatements({ limit: 100 }) : null,
    enabled: !!selectedCompanyId,
  });

  // Calculate stats
  const totalEntities = entities?.length || 0;
  const totalVouchers = vouchers?.length || 0;
  const matchedTransactions = bankStatements?.filter(bs => bs.reconciliation_status === 'Matched').length || 0;
  const unmatchedTransactions = bankStatements?.filter(bs => bs.reconciliation_status === 'Unmatched').length || 0;
  const reconciliationRate = bankStatements?.length ? 
    Math.round((matchedTransactions / bankStatements.length) * 100) : 0;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        {selectedCompanyId && (
          <p className="text-sm text-gray-600">
            Viewing data for selected company
          </p>
        )}
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Companies"
          value={totalEntities}
          icon={BuildingOfficeIcon}
          color="bg-blue-500"
        />
        <StatCard
          title="Total Vouchers"
          value={totalVouchers}
          icon={DocumentTextIcon}
          color="bg-green-500"
        />
        <StatCard
          title="Reconciliation Rate"
          value={`${reconciliationRate}%`}
          icon={ChartBarIcon}
          color="bg-purple-500"
        />
        <StatCard
          title="Unmatched Transactions"
          value={unmatchedTransactions}
          icon={BanknotesIcon}
          color="bg-red-500"
        />
      </div>

      {!selectedCompanyId && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">
                No Company Selected
              </h3>
              <div className="mt-2 text-sm text-yellow-700">
                <p>
                  Please select a company from the dropdown above to view detailed financial data and perform reconciliation operations.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {selectedCompanyId && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Vouchers */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Vouchers</h3>
            <div className="space-y-3">
              {vouchers?.slice(0, 5).map((voucher) => (
                <div key={voucher.voucher_id} className="flex justify-between items-center py-2 border-b border-gray-100">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{voucher.voucher_number}</p>
                    <p className="text-xs text-gray-500">{voucher.voucher_type}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">₹{voucher.total_amount.toLocaleString()}</p>
                    <p className="text-xs text-gray-500">{new Date(voucher.voucher_date).toLocaleDateString()}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Reconciliation Status */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Reconciliation Status</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Matched</span>
                <span className="text-sm font-medium text-green-600">{matchedTransactions}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Unmatched</span>
                <span className="text-sm font-medium text-red-600">{unmatchedTransactions}</span>
              </div>
              <div className="pt-2 border-t border-gray-100">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-900">Total</span>
                  <span className="text-sm font-medium text-gray-900">{bankStatements?.length || 0}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}