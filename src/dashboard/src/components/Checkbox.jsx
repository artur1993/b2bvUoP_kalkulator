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
        className="mr-2 leading-tight"
        {...props}
      />
      <label htmlFor={id} className="text-gray-700 text-sm">
        {label}
      </label>
    </div>
  );
};

export default Checkbox;
