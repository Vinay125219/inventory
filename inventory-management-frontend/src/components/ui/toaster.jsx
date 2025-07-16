import React from 'react';

export const Toaster = () => {
  return null; // Placeholder for toast notifications
};

export const useToast = () => {
  const toast = ({ title, description, variant = 'default' }) => {
    console.log('Toast:', { title, description, variant });
  };

  return { toast };
};

