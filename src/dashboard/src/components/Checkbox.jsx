import React from 'react';

const Checkbox = ({ label, id, checked, onChange, ...props }) => {
  return (
    <div className="mb-4 flex items-center">
      <input
        type="checkbox"
        id={id}
        name={id}
        checked={checked}
        onChange={onChange}
        className="mr-2 h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded transition duration-200"
        {...props}
      />
      <label htmlFor={id} className="text-gray-700 text-sm">
        {label}
      </label>
    </div>
  );
};

export default Checkbox;
