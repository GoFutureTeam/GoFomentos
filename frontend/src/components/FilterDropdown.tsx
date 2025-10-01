import React, { useState } from 'react';
interface FilterOption {
  id: string;
  label: string;
  checked: boolean;
}
interface FilterDropdownProps {
  title: string;
  options: FilterOption[];
  onFilterChange: (optionId: string, checked: boolean) => void;
  onSelectAll?: (selectAll: boolean) => void;
  iconSrc: string;
}
const FilterDropdown: React.FC<FilterDropdownProps> = ({
  title,
  options,
  onFilterChange,
  onSelectAll,
  iconSrc
}) => {
  const handleCheckboxChange = (optionId: string, checked: boolean) => {
    onFilterChange(optionId, checked);
  };

  const handleSelectAll = (checked: boolean) => {
    if (onSelectAll) {
      onSelectAll(checked);
    }
  };

  const allSelected = options.length > 0 && options.every(option => option.checked);

  return <div className="flex flex-col items-stretch">
      <div className="text-[#435058] font-extrabold text-[15px] whitespace-nowrap">
        <span className="text-[#435058] text-lg  font-extrabold py-0 ">{title}</span>
      </div>
      <div className={`flex w-full flex-col items-stretch text-foreground font-medium mt-[18px] pl-4 ${options.length > 5 ? 'max-h-[200px] overflow-y-auto' : ''}`}>
        {onSelectAll && (
          <label className="flex items-stretch gap-2 cursor-pointer rounded-sm">
            <input 
              type="checkbox" 
              checked={allSelected} 
              onChange={e => handleSelectAll(e.target.checked)} 
              className="sr-only" 
            />
            <div className={`border flex w-[18px] shrink-0 h-[17px] rounded-[5px] border-black border-solid ${allSelected ? 'bg-[rgb(220,247,99)]' : ''}`} />
            <span className="basis-auto text-sm font-bold">Todos</span>
          </label>
        )}
        {options.map(option => <label key={option.id} className="flex items-stretch gap-2 mt-[15px] first:mt-0 cursor-pointer rounded-sm">
            <input type="checkbox" checked={option.checked} onChange={e => handleCheckboxChange(option.id, e.target.checked)} className="sr-only" />
            <div className={`border flex w-[18px] shrink-0 h-[17px] rounded-[5px] border-black border-solid ${option.checked ? 'bg-[rgb(220,247,99)]' : ''}`} />
            <span className="basis-auto text-sm ">{option.label}</span>
          </label>)}
      </div>
    </div>;
};
export default FilterDropdown;