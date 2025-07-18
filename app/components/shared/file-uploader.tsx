'use client';

import React, { useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Upload, X, File } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useFileUpload } from '@/hooks';
import type { FileUploaderProps } from '@/types';

export function FileUploader({
  accept,
  onChange,
  placeholder = 'Click to upload or drag and drop',
  disabled = false,
  className,
}: FileUploaderProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const {
    file,
    isDragOver,
    handleFileSelect,
    clearFile: clearFileHook,
    handleDragOver,
    handleDragLeave,
    handleDrop,
  } = useFileUpload({
    acceptedFormats: accept,
    onError: (error) => console.error('File upload error:', error),
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0] || null;
    handleFileSelect(selectedFile);
    onChange(selectedFile);
  };

  const handleDropWrapper = (e: React.DragEvent) => {
    handleDrop(e);
    if (file) onChange(file);
  };

  const clearFile = () => {
    clearFileHook();
    onChange(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className={cn('space-y-2', className)}>
      <div
        className={cn(
          'relative border-2 border-dashed rounded-lg p-6 transition-colors cursor-pointer glass-card',
          isDragOver && !disabled
            ? 'border-blue-400 bg-blue-50/10'
            : 'border-gray-300',
          disabled ? 'opacity-50 cursor-not-allowed' : 'hover:border-gray-400'
        )}
        onDrop={handleDropWrapper}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => !disabled && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={accept}
          onChange={handleFileChange}
          disabled={disabled}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />

        <div className="flex flex-col items-center justify-center space-y-2">
          {file ? (
            <>
              <File className="h-8 w-8 text-blue-500" />
              <div className="text-center">
                <p className="text-sm font-medium text-foreground">
                  {file.name}
                </p>
                <p className="text-xs text-muted-foreground">
                  {(file.size / 1024).toFixed(1)} KB
                </p>
              </div>
            </>
          ) : (
            <>
              <Upload
                className={cn(
                  'h-8 w-8',
                  isDragOver ? 'text-blue-500' : 'text-muted-foreground'
                )}
              />
              <div className="text-center">
                <p className="text-sm font-medium text-foreground">
                  {placeholder}
                </p>
                <p className="text-xs text-muted-foreground">
                  {accept ? `Accepted formats: ${accept}` : 'Any file type'}
                </p>
              </div>
            </>
          )}
        </div>
      </div>

      {file && (
        <div className="flex items-center justify-between">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={clearFile}
            disabled={disabled}
            className="flex items-center gap-2"
          >
            <X className="h-3 w-3" />
            Clear file
          </Button>
        </div>
      )}
    </div>
  );
}
