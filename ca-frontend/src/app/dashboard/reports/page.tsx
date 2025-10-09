'use client';

import { useState, useEffect } from 'react';
import { 
  ChartBarIcon,
  DocumentChartBarIcon,
  CursorArrowRaysIcon,
  BanknotesIcon,
  ClipboardDocumentListIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  CalendarDaysIcon,
  FunnelIcon
} from '@heroicons/react/24/outline';
import { useAuthStore } from '@/store/auth';
import { UserRole } from '@/types/api';

interface ReportSummary {
  total_vouchers: number;
  total_amount: number;
  matched_records: number;
  unmatched_records: number;
  reconciliation_rate: number;
  period_start: string;
  period_end: string;
}

interface VoucherTypeStats {
  voucher_type: string;
  count: number;
  total_amount: number;
  percentage: number;
}

interface ReconciliationStats {
  status: string;
  count: number;
  percentage: number;
  total_amount: number;
}

interface MonthlyTrend {
  month: string;
  vouchers: number;
  amount: number;
  reconciled: number;
}

export default function ReportsPage() {
  const { user, token, selectedCompanyId } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [activeReport, setActiveReport] = useState<'summary' | 'reconciliation' | 'trends' | 'voucher-analysis'>('summary');
  
  // Report data
  const [summary, setSummary] = useState<ReportSummary | null>(null);
  const [voucherStats, setVoucherStats] = useState<VoucherTypeStats[]>([]);
  const [reconciliationStats, setReconciliationStats] = useState<ReconciliationStats[]>([]);
  const [monthlyTrends, setMonthlyTrends] = useState<MonthlyTrend[]>([]);
  
  // Filters
  const [dateRange, setDateRange] = useState({
    start: new Date(new Date().getFullYear(), new Date().getMonth() - 3, 1).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    if (selectedCompanyId) {
      loadReports();
    }
  }, [selectedCompanyId, dateRange]);

  const loadReports = async () => {
    if (!selectedCompanyId) return;
    
    setLoading(true);
    try {
      await Promise.all([
        loadSummaryReport(),
        loadVoucherStats(),
        loadReconciliationStats(),
        loadMonthlyTrends()
      ]);
    } catch (error) {
      console.error('Error loading reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSummaryReport = async () => {
    try {
      const response = await fetch(`/api/v1/cdm/vouchers?from_date=${dateRange.start}&to_date=${dateRange.end}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Company-ID': selectedCompanyId!,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const vouchers = await response.json();
        
        // Calculate summary statistics
        const totalAmount = vouchers.reduce((sum: number, v: any) => sum + parseFloat(v.total_amount || 0), 0);
        const matchedCount = vouchers.filter((v: any) => v.reconciliation_status === 'AutoMatched' || v.reconciliation_status === 'ManuallyVerified').length;
        const unmatchedCount = vouchers.filter((v: any) => v.reconciliation_status === 'Unmatched').length;
        const reconciliationRate = vouchers.length > 0 ? (matchedCount / vouchers.length) * 100 : 0;

        setSummary({
          total_vouchers: vouchers.length,
          total_amount: totalAmount,
          matched_records: matchedCount,
          unmatched_records: unmatchedCount,
          reconciliation_rate: reconciliationRate,
          period_start: dateRange.start,
          period_end: dateRange.end
        });
      }
    } catch (error) {
      console.error('Error loading summary:', error);
    }
  };

  const loadVoucherStats = async () => {
    try {
      const response = await fetch(`/api/v1/cdm/vouchers?from_date=${dateRange.start}&to_date=${dateRange.end}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Company-ID': selectedCompanyId!,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const vouchers = await response.json();
        
        // Group by voucher type
        const typeGroups = vouchers.reduce((acc: any, voucher: any) => {
          const type = voucher.voucher_type || 'Unknown';
          if (!acc[type]) {
            acc[type] = { count: 0, total_amount: 0 };
          }
          acc[type].count += 1;
          acc[type].total_amount += parseFloat(voucher.total_amount || 0);
          return acc;
        }, {});

        const totalAmount = Object.values(typeGroups).reduce((sum: number, group: any) => sum + group.total_amount, 0);
        
        const stats = Object.entries(typeGroups).map(([type, data]: [string, any]) => ({
          voucher_type: type,
          count: data.count,
          total_amount: data.total_amount,
          percentage: totalAmount > 0 ? (data.total_amount / totalAmount) * 100 : 0
        }));

        setVoucherStats(stats);
      }
    } catch (error) {
      console.error('Error loading voucher stats:', error);
    }
  };

  const loadReconciliationStats = async () => {
    try {
      const response = await fetch(`/api/v1/cdm/vouchers?from_date=${dateRange.start}&to_date=${dateRange.end}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Company-ID': selectedCompanyId!,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const vouchers = await response.json();
        
        // Group by reconciliation status
        const statusGroups = vouchers.reduce((acc: any, voucher: any) => {
          const status = voucher.reconciliation_status || 'Unmatched';
          if (!acc[status]) {
            acc[status] = { count: 0, total_amount: 0 };
          }
          acc[status].count += 1;
          acc[status].total_amount += parseFloat(voucher.total_amount || 0);
          return acc;
        }, {});

        const totalCount = vouchers.length;
        const totalAmount = Object.values(statusGroups).reduce((sum: number, group: any) => sum + group.total_amount, 0);
        
        const stats = Object.entries(statusGroups).map(([status, data]: [string, any]) => ({
          status,
          count: data.count,
          percentage: totalCount > 0 ? (data.count / totalCount) * 100 : 0,
          total_amount: data.total_amount
        }));

        setReconciliationStats(stats);
      }
    } catch (error) {
      console.error('Error loading reconciliation stats:', error);
    }
  };

  const loadMonthlyTrends = async () => {
    try {
      const response = await fetch(`/api/v1/cdm/vouchers?from_date=${dateRange.start}&to_date=${dateRange.end}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Company-ID': selectedCompanyId!,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const vouchers = await response.json();
        
        // Group by month
        const monthGroups = vouchers.reduce((acc: any, voucher: any) => {
          const date = new Date(voucher.voucher_date);
          const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
          
          if (!acc[monthKey]) {
            acc[monthKey] = { vouchers: 0, amount: 0, reconciled: 0 };
          }
          
          acc[monthKey].vouchers += 1;
          acc[monthKey].amount += parseFloat(voucher.total_amount || 0);
          
          if (voucher.reconciliation_status === 'AutoMatched' || voucher.reconciliation_status === 'ManuallyVerified') {
            acc[monthKey].reconciled += 1;
          }
          
          return acc;
        }, {});

        const trends = Object.entries(monthGroups)
          .map(([month, data]: [string, any]) => ({
            month: new Date(month + '-01').toLocaleString('default', { month: 'short', year: 'numeric' }),
            vouchers: data.vouchers,
            amount: data.amount,
            reconciled: data.reconciled
          }))
          .sort((a, b) => a.month.localeCompare(b.month));

        setMonthlyTrends(trends);
      }
    } catch (error) {
      console.error('Error loading monthly trends:', error);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatPercentage = (percentage: number) => {
    return `${percentage.toFixed(1)}%`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Reports & Analytics</h1>
          <p className="text-gray-600 dark:text-gray-400">Financial insights and reconciliation analytics</p>
        </div>
        
        {/* Date Range Filter */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <CalendarDaysIcon className="h-5 w-5 text-gray-400" />
            <input
              type="date"
              value={dateRange.start}
              onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
            <span className="text-gray-500">to</span>
            <input
              type="date"
              value={dateRange.end}
              onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Report Navigation */}
      <div className="bg-white border-b border-gray-200">
        <nav className="flex space-x-8">
          {[
            { id: 'summary', label: 'Summary', icon: ChartBarIcon },
            { id: 'reconciliation', label: 'Reconciliation', icon: CursorArrowRaysIcon },
            { id: 'trends', label: 'Trends', icon: ArrowTrendingUpIcon },
            { id: 'voucher-analysis', label: 'Voucher Analysis', icon: DocumentChartBarIcon },
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveReport(tab.id as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeReport === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-5 w-5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Summary Report */}
      {activeReport === 'summary' && summary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Vouchers</p>
                <p className="text-3xl font-bold text-gray-900">{summary.total_vouchers.toLocaleString()}</p>
              </div>
              <ClipboardDocumentListIcon className="h-12 w-12 text-blue-500" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Amount</p>
                <p className="text-3xl font-bold text-gray-900">{formatCurrency(summary.total_amount)}</p>
              </div>
              <BanknotesIcon className="h-12 w-12 text-green-500" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Reconciliation Rate</p>
                <p className="text-3xl font-bold text-gray-900">{formatPercentage(summary.reconciliation_rate)}</p>
              </div>
              <CheckCircleIcon className="h-12 w-12 text-emerald-500" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Unmatched Records</p>
                <p className="text-3xl font-bold text-gray-900">{summary.unmatched_records.toLocaleString()}</p>
              </div>
              <ExclamationTriangleIcon className="h-12 w-12 text-amber-500" />
            </div>
          </div>
        </div>
      )}

      {/* Reconciliation Report */}
      {activeReport === 'reconciliation' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Reconciliation Status</h3>
            <div className="space-y-4">
              {reconciliationStats.map((stat) => (
                <div key={stat.status} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      stat.status === 'AutoMatched' || stat.status === 'ManuallyVerified' 
                        ? 'bg-green-100 text-green-800'
                        : stat.status === 'Disputed'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {stat.status}
                    </span>
                    <span className="text-sm text-gray-600">{stat.count} records</span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-gray-900">{formatPercentage(stat.percentage)}</div>
                    <div className="text-xs text-gray-500">{formatCurrency(stat.total_amount)}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Reconciliation Progress</h3>
            <div className="space-y-4">
              {reconciliationStats.map((stat) => (
                <div key={stat.status}>
                  <div className="flex justify-between text-sm font-medium">
                    <span>{stat.status}</span>
                    <span>{formatPercentage(stat.percentage)}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        stat.status === 'AutoMatched' || stat.status === 'ManuallyVerified' 
                          ? 'bg-green-500'
                          : stat.status === 'Disputed'
                          ? 'bg-red-500'
                          : 'bg-yellow-500'
                      }`}
                      style={{ width: `${stat.percentage}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Monthly Trends */}
      {activeReport === 'trends' && (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Monthly Trends</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Month
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Vouchers
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Reconciled
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rate
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {monthlyTrends.map((trend) => (
                  <tr key={trend.month}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {trend.month}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {trend.vouchers.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatCurrency(trend.amount)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {trend.reconciled.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatPercentage(trend.vouchers > 0 ? (trend.reconciled / trend.vouchers) * 100 : 0)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Voucher Analysis */}
      {activeReport === 'voucher-analysis' && (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Voucher Type Analysis</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Voucher Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Count
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Total Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Percentage
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {voucherStats.map((stat) => (
                  <tr key={stat.voucher_type}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {stat.voucher_type}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {stat.count.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatCurrency(stat.total_amount)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                          <div 
                            className="bg-blue-500 h-2 rounded-full"
                            style={{ width: `${stat.percentage}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-500">{formatPercentage(stat.percentage)}</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* No Company Selected */}
      {!selectedCompanyId && (
        <div className="text-center py-12">
          <FunnelIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No Company Selected</h3>
          <p className="mt-1 text-sm text-gray-500">
            Please select a company to view reports and analytics
          </p>
        </div>
      )}
    </div>
  );
}