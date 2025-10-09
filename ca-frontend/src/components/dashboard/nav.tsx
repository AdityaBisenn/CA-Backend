'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  HomeIcon,
  BuildingOfficeIcon,
  DocumentTextIcon,
  BanknotesIcon,
  ChartBarIcon,
  CogIcon,
  UsersIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import { useAuthStore, hasStaffAccess, isFirmAdmin } from '@/store/auth';

interface NavItemProps {
  href: string;
  icon: React.ComponentType<any>;
  label: string;
  isCollapsed: boolean;
  isActive: boolean;
}

function NavItem({ href, icon: Icon, label, isCollapsed, isActive }: NavItemProps) {
  return (
    <Link
      href={href}
      className={`flex items-center px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ${
        isActive ? 'bg-blue-50 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 border-r-2 border-blue-700 dark:border-blue-400' : 'text-gray-700 dark:text-gray-300'
      }`}
    >
      <Icon className="h-5 w-5 flex-shrink-0" />
      {!isCollapsed && <span className="ml-3">{label}</span>}
    </Link>
  );
}

interface DashboardNavProps {
  isCollapsed: boolean;
}

export function DashboardNav({ isCollapsed }: DashboardNavProps) {
  const pathname = usePathname();
  const user = useAuthStore((state) => state.user);

  const navigationItems = [
    { href: '/dashboard', icon: HomeIcon, label: 'Dashboard', roles: ['all'] },
    { href: '/dashboard/entities', icon: BuildingOfficeIcon, label: 'Companies', roles: ['staff'] },
    { href: '/dashboard/vouchers', icon: DocumentTextIcon, label: 'Vouchers', roles: ['staff'] },
    { href: '/dashboard/reconciliation', icon: ArrowPathIcon, label: 'Reconciliation', roles: ['staff'] },
    { href: '/dashboard/reports', icon: ChartBarIcon, label: 'Reports', roles: ['staff'] },
    { href: '/dashboard/users', icon: UsersIcon, label: 'Users', roles: ['admin'] },
    { href: '/dashboard/settings', icon: CogIcon, label: 'Settings', roles: ['admin'] },
  ];

  const visibleItems = navigationItems.filter(item => {
    if (item.roles.includes('all')) return true;
    if (item.roles.includes('staff') && hasStaffAccess(user)) return true;
    if (item.roles.includes('admin') && isFirmAdmin(user)) return true;
    return false;
  });

  return (
    <nav className="mt-8 space-y-1">
      {visibleItems.map((item) => (
        <NavItem
          key={item.href}
          href={item.href}
          icon={item.icon}
          label={item.label}
          isCollapsed={isCollapsed}
          isActive={pathname === item.href}
        />
      ))}
    </nav>
  );
}