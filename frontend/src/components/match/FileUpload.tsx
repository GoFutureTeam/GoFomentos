import React, { useCallback, useState } from 'react';

interface FileUploadProps {
  onFileSelect: (file: File | null) => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onFileSelect }) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === 'application/pdf' && file.size <= 10 * 1024 * 1024) {
        setSelectedFile(file);
        onFileSelect(file);
      }
    }
  }, [onFileSelect]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.type === 'application/pdf' && file.size <= 10 * 1024 * 1024) {
        setSelectedFile(file);
        onFileSelect(file);
      }
    }
  }, [onFileSelect]);

  return (
    <label 
      htmlFor="file-upload"
      className={`bg-neutral-50 shadow-[0px_4px_6px_2px_rgba(0,0,0,0.25)] border self-stretch flex flex-col items-center justify-center mt-[25px] px-12 py-6 rounded-[35px] border-black border-dashed max-md:max-w-full max-md:px-5 transition-colors cursor-pointer hover:bg-neutral-100 ${
        dragActive ? 'border-[rgba(67,80,88,1)] bg-[rgba(67,80,88,1)]/10' : ''
      }`}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <div className="flex w-[400px] max-w-full flex-col items-center">
        <img
          src="https://api.builder.io/api/v1/image/assets/f302f4804c934a9ca3c4b476c31d8232/a6125ba0ca02f06e93abb71eae3cf06a5bbd32cd?placeholderIfAbsent=true"
          alt="Upload icon"
          className="aspect-[1] object-contain w-[48px]"
        />
        <div className="flex items-center justify-center text-[rgba(67,80,88,1)] mt-2 whitespace-nowrap">
          <span className="font-bold hover:text-[rgba(67,80,88,0.8)] transition-colors">
            Carregue um arquivo
          </span>
          <span className="font-medium ml-2">
            ou arraste e solte
          </span>
        </div>
        <p className="text-black font-medium text-center mt-3">
          {selectedFile ? selectedFile.name : 'PDF até 10MB'}
        </p>
      </div>
      <input
        id="file-upload"
        type="file"
        accept=".pdf"
        onChange={handleFileInput}
        className="hidden"
        aria-label="Upload PDF file"
      />
    </label>
  );
};