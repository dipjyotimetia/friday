'use client';

import { useCallback } from 'react';
import { useToast } from '@/components/shared/toast-provider';
import { APIError, ValidationError } from '@/services/api';

interface UseApiErrorOptions {
  showToast?: boolean;
  defaultErrorMessage?: string;
}

export function useApiError(options: UseApiErrorOptions = {}) {
  const {
    showToast = true,
    defaultErrorMessage = 'An unexpected error occurred',
  } = options;
  const { addToast } = useToast();

  const handleError = useCallback(
    (error: unknown, context?: string) => {
      console.error('API Error:', error);

      let title = defaultErrorMessage;
      let description: string | undefined;
      let actionLabel: string | undefined;
      let actionHandler: (() => void) | undefined;

      if (error instanceof ValidationError) {
        title = 'Validation Error';
        description = error.errors
          .map((e) => `${e.field ? e.field + ': ' : ''}${e.message}`)
          .join(', ');
      } else if (error instanceof APIError) {
        title = error.message;
        description = error.details ? JSON.stringify(error.details) : undefined;

        if (error.statusCode === 429) {
          title = 'Rate Limited';
          description = 'Too many requests. Please try again later.';
          actionLabel = 'Retry';
          actionHandler = () => window.location.reload();
        } else if (error.statusCode === 0) {
          title = 'Network Error';
          description =
            'Unable to connect to the server. Please check your connection.';
          actionLabel = 'Retry';
          actionHandler = () => window.location.reload();
        }
      } else if (error instanceof Error) {
        title = error.message;
      }

      if (context) {
        title = `${context}: ${title}`;
      }

      if (showToast) {
        addToast({
          type: 'error',
          title,
          description,
          duration: 6000,
          action:
            actionLabel && actionHandler
              ? {
                  label: actionLabel,
                  onClick: actionHandler,
                }
              : undefined,
        });
      }

      return {
        title,
        description,
        isValidationError: error instanceof ValidationError,
        isAPIError: error instanceof APIError,
        statusCode: error instanceof APIError ? error.statusCode : undefined,
        requestId: error instanceof APIError ? error.requestId : undefined,
      };
    },
    [addToast, defaultErrorMessage, showToast]
  );

  const showSuccess = useCallback(
    (message: string, description?: string) => {
      if (showToast) {
        addToast({
          type: 'success',
          title: message,
          description,
          duration: 4000,
        });
      }
    },
    [addToast, showToast]
  );

  const showWarning = useCallback(
    (message: string, description?: string) => {
      if (showToast) {
        addToast({
          type: 'warning',
          title: message,
          description,
          duration: 5000,
        });
      }
    },
    [addToast, showToast]
  );

  const showInfo = useCallback(
    (message: string, description?: string) => {
      if (showToast) {
        addToast({
          type: 'info',
          title: message,
          description,
          duration: 4000,
        });
      }
    },
    [addToast, showToast]
  );

  return {
    handleError,
    showSuccess,
    showWarning,
    showInfo,
  };
}
