'use client';

import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '@/store/auth';
import { cdmService } from '@/services/cdm';
import { ChevronDownIcon } from '@heroicons/react/24/outline';

export function CompanySelector() {
  const { selectedCompanyId, setSelectedCompany } = useAuthStore();
  const [isOpen, setIsOpen] = useState(false);

  const { data: entities, isLoading } = useQuery({
    queryKey: ['entities'],
    queryFn: () => cdmService.getEntities({ limit: 100 }),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const selectedEntity = entities?.find(entity => entity.company_id === selectedCompanyId);

  const handleSelectCompany = (companyId: string) => {
    setSelectedCompany(companyId);
    setIsOpen(false);
  };

  if (isLoading) {
    return (
      <div className="animate-pulse bg-gray-200 h-8 w-48 rounded"></div>
    );
  }

  return (
    <div className="relative">
      <button
        type="button"
        className="bg-white border border-gray-300 rounded-md px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 flex items-center space-x-2"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span>
          {selectedEntity ? selectedEntity.company_name : 'Select Company'}
        </span>
        <ChevronDownIcon className="h-4 w-4" />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-white border border-gray-300 rounded-md shadow-lg z-10">
          <div className="py-1 max-h-60 overflow-y-auto">
            {entities?.map((entity) => (
              <button
                key={entity.company_id}
                className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                onClick={() => handleSelectCompany(entity.company_id)}
              >
                <div className="font-medium">{entity.company_name}</div>
                <div className="text-xs text-gray-500">{entity.gstin || 'No GSTIN'}</div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}