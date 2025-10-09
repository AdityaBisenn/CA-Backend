import * as React from "react"

interface ToastProps {
  children: React.ReactNode
}

export function Toaster({ children }: ToastProps) {
  return (
    <div id="toast-container" className="fixed bottom-4 right-4 z-50">
      {children}
    </div>
  )
}

export function useToast() {
  const toast = React.useCallback((message: string, type: 'success' | 'error' | 'info' = 'info') => {
    // Simple toast implementation - in a real app you'd use a proper toast library
    console.log(`Toast (${type}):`, message);
  }, []);

  return { toast };
}