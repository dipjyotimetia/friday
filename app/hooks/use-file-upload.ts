'use client';

import { useState, useCallback } from 'react';
import { FILE_CONFIG } from '@/config/constants';

interface UseFileUploadOptions {
  acceptedFormats?: string;
  maxSize?: number;
  onError?: (error: string) => void;
}

export function useFileUpload(options: UseFileUploadOptions = {}) {
  const {
    acceptedFormats = FILE_CONFIG.ACCEPTED_SPEC_FORMATS,
    maxSize = FILE_CONFIG.MAX_FILE_SIZE,
    onError,
  } = options;

  const [file, setFile] = useState<File | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const validateFile = useCallback(
    (file: File): string | null => {
      // Check file size
      if (file.size > maxSize) {
        return `File size must be less than ${Math.round(maxSize / 1024 / 1024)}MB`;
      }

      // Check file extension
      const extension = file.name.split('.').pop()?.toLowerCase();
      const acceptedExtensions = acceptedFormats
        .split(',')
        .map((format) => format.replace('.', '').trim());

      if (!extension || !acceptedExtensions.includes(extension)) {
        return `File must be one of: ${acceptedFormats}`;
      }

      return null;
    },
    [acceptedFormats, maxSize]
  );

  const handleFileSelect = useCallback(
    (selectedFile: File | null) => {
      if (!selectedFile) {
        setFile(null);
        return;
      }

      const validationError = validateFile(selectedFile);
      if (validationError) {
        onError?.(validationError);
        return;
      }

      setFile(selectedFile);
    },
    [validateFile, onError]
  );

  const clearFile = useCallback(() => {
    setFile(null);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);

      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile) {
        handleFileSelect(droppedFile);
      }
    },
    [handleFileSelect]
  );

  return {
    file,
    isDragOver,
    handleFileSelect,
    clearFile,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    validateFile,
  };
}
