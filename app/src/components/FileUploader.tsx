import React from 'react';

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
      <input
        type="file"
        id="file-upload"
        accept={accept}
        onChange={handleChange}
        disabled={disabled}
        className="hidden"
      />
      <label 
        htmlFor="file-upload" 
        className={`block w-full p-9 border-2 border-dashed rounded-xl text-center text-lg transition-all duration-300 ${
          disabled 
            ? 'border-primary-600 bg-primary-700 text-primary-400 cursor-not-allowed opacity-60' 
            : 'border-accent-500 bg-primary-700 text-primary-100 cursor-pointer hover:bg-accent-500/5 hover:-translate-y-1 hover:shadow-glow active:scale-95'
        }`}
      >
        {placeholder}
      </label>
    </div>
  );
};
