import React, { useState } from "react";

/**
 * A reusable Tooltip component that displays a pop-up with text when hovered over its children.
 * @param {object} props - The component props.
 * @param {string} props.text - The text content to display inside the tooltip.
 * @param {React.ReactNode} props.children - The child elements that trigger the tooltip on hover.
 */
const Tooltip = ({ text, children }) => {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div
      className="relative flex items-center"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      {children}
      {isVisible && (
        <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 w-64 p-2 bg-gray-800 text-white text-sm rounded-md shadow-lg z-10">
          {text}
          <div className="absolute left-1/2 -translate-x-1/2 top-full w-0 h-0 border-x-8 border-x-transparent border-t-8 border-t-gray-800"></div>
        </div>
      )}
    </div>
  );
};

export default Tooltip;
