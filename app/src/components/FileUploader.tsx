import React from 'react';
import { FileInput, FileLabel } from '../css/friday';

interface FileUploaderProps {
    accept?: string;
    onChange: (file: File | null) => void;
    placeholder?: string;
    disabled?: boolean;
  }

  export const FileUploader: React.FC<FileUploaderProps> = ({
    accept,
    onChange,
    placeholder = 'Click to upload file',
    disabled = false,
}) => {
    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0] || null;
      onChange(file);
    };

    return (
      <div>
        <FileInput
          type="file"
          id="file-upload"
          accept={accept}
          onChange={handleChange}
          disabled={disabled}
        />
        <FileLabel htmlFor="file-upload" $disabled={disabled}>
          {placeholder}
        </FileLabel>
      </div>
    );
  };