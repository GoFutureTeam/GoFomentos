import React from 'react';
import { Toaster } from '@/components/ui/toaster';
import { Toaster as SonnerToaster } from '@/components/ui/sonner';

/**
 * Componente que fornece notificações toast para toda a aplicação
 * Centraliza os provedores de toast para garantir consistência
 */
export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <>
      {children}
      <Toaster />
      <SonnerToaster 
        position="top-right"
        toastOptions={{
          style: {
            background: 'white',
            color: 'black',
            border: '1px solid #e2e8f0',
          },
          classNames: {
            toast: 'group',
            title: 'font-medium text-gray-900',
            description: 'text-gray-500 text-sm',
            actionButton: 'bg-primary text-primary-foreground',
            cancelButton: 'bg-muted text-muted-foreground',
            error: '!bg-red-50 border-red-200',
            success: '!bg-green-50 border-green-200',
            warning: '!bg-yellow-50 border-yellow-200',
            info: '!bg-blue-50 border-blue-200',
          },
        }}
      />
    </>
  );
};
