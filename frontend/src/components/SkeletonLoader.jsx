import React from "react";

const SkeletonLoader = () => {
  return (
    <div
      className="mt-8 p-6 bg-surface rounded-xl shadow-lg animate-pulse"
      data-testid="skeleton-loader"
    >
      <div className="h-8 bg-gray-300 rounded w-3/4 mb-6"></div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-gray-200 p-6 rounded-lg h-64"></div>
        <div className="bg-gray-200 p-6 rounded-lg h-64"></div>
      </div>
      <div className="h-10 bg-gray-300 rounded w-1/2 mt-8 mx-auto"></div>
    </div>
  );
};

export default SkeletonLoader;
