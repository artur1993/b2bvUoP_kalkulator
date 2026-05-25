import React from "react";
import Tooltip from "./Tooltip";

/**
 * A reusable Select (dropdown) component for forms.
 * @param {object} props - The component props.
 * @param {string} props.label - The label for the select field.
 * @param {string} props.id - The unique ID for the select field.
 * @param {string} props.value - The current selected value of the select field.
 * @param {function} props.onChange - The event handler for select changes.
 * @param {Array<object>} props.options - An array of option objects, each with a 'value', 'label', and optional 'tooltip'.
 * @param {string} [props.description] - Optional description text for accessibility.
 * @param {object} props - Additional props to pass to the select element.
 */
const Select = ({
  label,
  id,
  value,
  onChange,
  options,
  description,
  ...props
}) => {
  const descriptionId = description ? `${id}-description` : undefined;

  return (
    <div className="mb-4">
      <label
        htmlFor={id}
        className="block text-gray-700 text-sm font-bold mb-2"
      >
        {label}
      </label>
      <select
        id={id}
        name={id}
        value={value}
        onChange={onChange}
        className="shadow-sm appearance-none border border-gray-300 rounded-md w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition duration-200"
        aria-label={label}
        aria-describedby={descriptionId}
        {...props}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {description && (
        <p id={descriptionId} className="text-medium-contrast text-xs mt-1">
          {description}
        </p>
      )}
      {options.map(
        (option) =>
          option.tooltip &&
          value === option.value && (
            <Tooltip key={option.value} text={option.tooltip}>
              <span className="text-xs text-medium-contrast ml-2">?</span>
            </Tooltip>
          ),
      )}
    </div>
  );
};

export default Select;
